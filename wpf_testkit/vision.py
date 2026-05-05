"""wpf_testkit/vision.py — 多模态大模型视觉分析模块

提供多模型供应商的统一接口，通过 Provider Adapter 模式解耦。
核心概念：
- VisionAnalyzer — 高层 API，封装截图分析和坐标定位
- VisionProvider — 底层适配器接口，对接不同多模态模型 API
- OpenAIVisionProvider — OpenAI 兼容格式的适配器（阿里百炼、MiniMax、DeepSeek 等）

使用方式：
    from wpf_testkit.vision import VisionAnalyzer

    va = VisionAnalyzer()
    if va.available:
        result = va.analyze(img, "描述这个窗口")
        print(result)

更换模型供应商只需切换 provider：
    from wpf_testkit.vision import VisionAnalyzer, OpenAIVisionProvider

    provider = OpenAIVisionProvider(
        api_url="https://api.minimaxi.com/v1/chat/completions",
        api_key="mm-xxx",
        model="minimax-vl-01",
    )
    va = VisionAnalyzer(provider=provider)
"""

from __future__ import annotations

import os
import time
from typing import Optional, Dict, Any, Protocol


# ── 可选导入（无依赖时降级） ──
_has_vision_deps = False
try:
    import base64
    import io
    import requests
    from PIL import Image, ImageGrab

    _has_vision_deps = True
except ImportError:
    pass


# ════════════════════════════════════════════════════════════
# Provider 接口
# ════════════════════════════════════════════════════════════


class VisionProvider(Protocol):
    """多模态视觉模型供应商适配器接口。

    实现此 Protocol 即可对接任意多模态模型 API。
    VisionAnalyzer 通过此接口调用底层模型，不感知具体供应商细节。
    """

    @property
    def available(self) -> bool:
        """Provider 是否可用（依赖已装 + 配置就绪）。"""
        ...

    def analyze(
        self, img, prompt: str, max_tokens: int = 1024, detail: str = "high"
    ) -> Optional[str]:
        """分析截图，返回文本描述。

        参数:
            img: PIL Image 对象
            prompt: 分析提示词
            max_tokens: 最大输出 token
            detail: 图片细节级别 ("high" / "low")
        """
        ...

    def healthy_check(self) -> bool:
        """快速检测 API 可用性（发送极简请求验证链路）。"""
        ...


# ════════════════════════════════════════════════════════════
# OpenAI 兼容格式 Provider
# ════════════════════════════════════════════════════════════


class OpenAIVisionProvider:
    """OpenAI 兼容格式的多模态 API 适配器。

    适用于所有兼容 OpenAI /v1/chat/completions 格式的供应商：
    - 阿里百炼（Qwen2.5-VL）
    - MiniMax（mini-max-vl-01）
    - DeepSeek（deepseek-vl2）
    - 智谱 GLM-4V
    - OpenAI 自身（gpt-4o / gpt-4-vision）
    - 任何使用 messages+image_url 格式的 API

    认证方式支持：
    - Bearer Token（Authorization 头，默认）
    - 自定义 Header（通过 extra_headers 参数）

    使用示例：
        provider = OpenAIVisionProvider(
            api_url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            api_key="sk-xxx",
            model="qwen2.5-vl-72b-instruct",
        )
        va = VisionAnalyzer(provider=provider)
    """

    def __init__(
        self,
        api_url: str = "",
        api_key: str = "",
        model: str = "qwen2.5-vl-72b-instruct",
        timeout: float = 30.0,
        temperature: float = 0.1,
        auth_header: str = "Bearer",
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.auth_header = auth_header
        self.extra_headers = extra_headers or {}
        self._enabled = self._auto_detect()

    def _auto_detect(self) -> bool:
        if not _has_vision_deps:
            return False
        if not self.api_key or self.api_key == "":
            return False
        if len(self.api_key) < 10:
            return False
        if not self.api_url:
            return False
        return True

    @property
    def available(self) -> bool:
        return self._enabled

    def _image_to_base64(self, img) -> str:
        """PIL Image → base64（JPEG quality 85）。"""
        if not isinstance(img, Image.Image):
            raise TypeError(f"需要 PIL.Image, 收到 {type(img).__name__}")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def analyze(
        self, img, prompt: str, max_tokens: int = 1024, detail: str = "high"
    ) -> Optional[str]:
        """向 OpenAI 兼容 API 发送截图+文本，返回 AI 描述。"""
        if not self._enabled:
            return None

        b64 = self._image_to_base64(img)
        data_url = f"data:image/jpeg;base64,{b64}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url, "detail": detail},
                        },
                    ],
                }
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }

        headers = {
            "Authorization": f"{self.auth_header} {self.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.extra_headers)

        try:
            resp = requests.post(
                self.api_url, headers=headers, json=payload, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            try:
                detail_text = f"HTTP {resp.status_code}: {resp.text[:300]}"
            except Exception:
                detail_text = str(e)
            print(f"[OpenAIVisionProvider] HTTP 错误: {detail_text}")
            return None
        except Exception as e:
            print(f"[OpenAIVisionProvider] 调用失败: {e}")
            return None

    def healthy_check(self) -> bool:
        """快速检测 API 可用性。"""
        if not self._enabled:
            return False
        try:
            img = ImageGrab.grab(bbox=(0, 0, 100, 100))
        except Exception:
            return False

        b64 = self._image_to_base64(img)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这图中的内容是什么？"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"{self.auth_header} {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(
                self.api_url, headers=headers, json=payload, timeout=15
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"[OpenAIVisionProvider] 健康检测失败: {e}")
            self._enabled = False
            return False

    def __repr__(self) -> str:
        return f"OpenAIVisionProvider(model={self.model}, url={self.api_url})"


# ── 默认 Provider（阿里百炼 Qwen2.5-VL） ──

def _create_default_provider() -> OpenAIVisionProvider:
    """创建默认的阿里百炼 Qwen2.5-VL Provider。"""
    return OpenAIVisionProvider(
        api_url=os.environ.get(
            "VISION_API_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        ),
        api_key=os.environ.get("ALIYUN_VISION_API_KEY", ""),
        model=os.environ.get("VISION_MODEL", "qwen2.5-vl-72b-instruct"),
    )


# ════════════════════════════════════════════════════════════
# VisionAnalyzer — 高层 API
# ════════════════════════════════════════════════════════════


class VisionAnalyzer:
    """多模态视觉分析器。

    通过 Provider Adapter 对接任意多模态模型供应商。
    提供：截图分析、健康检测、控件坐标定位、双图语义比较等高层接口。

    不包含 WPF 场景专用的检测方法（如 verify_dialog、check_playing），
    这些应放在 BasePage 中或者单独的场景模块中。
    """

    def __init__(
        self,
        provider: Optional[VisionProvider] = None,
        enabled: Optional[bool] = None,
    ):
        self._provider = provider or _create_default_provider()

        if enabled is not None:
            # 显式覆盖
            self._enabled = enabled
        else:
            self._enabled = self._provider.available

    # ── 属性 ──

    @property
    def available(self) -> bool:
        return self._enabled

    @property
    def provider(self) -> VisionProvider:
        return self._provider

    # ── 核心 API ──

    def analyze(
        self, img, prompt: str, max_tokens: int = 1024, detail: str = "high"
    ) -> Optional[str]:
        """通用截图分析。"""
        if not self._enabled:
            return None
        return self._provider.analyze(img, prompt, max_tokens, detail)

    def healthy_check(self) -> bool:
        """健康检测。失败时自动禁用自身。"""
        if not self._enabled:
            return False
        ok = self._provider.healthy_check()
        if not ok:
            self._enabled = False
        return ok

    # ── 控件坐标定位 ──

    def find_control(self, img, description: str) -> Optional[str]:
        """通过描述定位控件坐标。

        参数:
            img: PIL Image
            description: 控件描述，如 "包含文字'保存'的按钮"

        返回:
            坐标字符串，如 "x_pct=50, y_pct=60"，未找到时返回含 "not_found" 的字符串
        """
        if not self._enabled:
            return None
        prompt = (
            f"在这张截图中找到{description}。\n"
            "给出它的中心相对坐标百分比，格式：x_pct=50, y_pct=60\n"
            "如果没有找到，回答：not_found\n"
        )
        return self._provider.analyze(img, prompt)

    def find_close_button(self, img) -> Optional[str]:
        """定位关闭按钮坐标。"""
        if not self._enabled:
            return None
        prompt = (
            "这张截图是一个桌面应用的弹窗。请分析：\n"
            "1. 右上角是否有 ✕ 关闭按钮？\n"
            "2. 如果有，给出相对坐标百分比，格式：x_pct=90, y_pct=5\n"
            "3. 如果没有 ✕ 按钮，是否有其他关闭方式？\n"
        )
        return self._provider.analyze(img, prompt)

    # ── 双图比较 ──

    def compare_semantic(
        self, candidate_img, baseline_img
    ) -> Optional[str]:
        """语义比较两张截图，描述实质性差异。

        将两张图左右拼接后发给模型分析，降低调用次数。
        """
        if not self._enabled:
            return None

        w = candidate_img.width + baseline_img.width
        h = max(candidate_img.height, baseline_img.height)
        combined = Image.new("RGB", (w, h), (0, 0, 0))
        combined.paste(candidate_img, (0, 0))
        combined.paste(baseline_img, (candidate_img.width, 0))

        prompt = (
            "这张图包含两张左右并排的截图，左侧是候选图，右侧是基准图。\n"
            "请分析：\n"
            "1. 两张图有哪些视觉上的差异？\n"
            "2. 这些差异是否影响功能？（忽略时间/日期/动画/滚动位置的正常变化）\n"
            "3. 如果是非功能性差异（仅时间变化、滚动位置、动画帧），请说明'非实质性差异'\n"
        )
        return self._provider.analyze(combined, prompt, max_tokens=512)


# ── 全局单例（延迟初始化） ──
_global_analyzer: Optional[VisionAnalyzer] = None


def get_analyzer(
    provider: Optional[VisionProvider] = None,
    enabled: Optional[bool] = None,
) -> VisionAnalyzer:
    """获取（或创建）全局 VisionAnalyzer 实例。

    延迟初始化 + 缓存单例。首次调用时自动检测依赖和密钥。
    可传入自定义 provider 覆盖默认的阿里百炼适配器。
    """
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = VisionAnalyzer(provider=provider, enabled=enabled)
    return _global_analyzer


def reset_analyzer():
    """重置全局分析器（测试用）。"""
    global _global_analyzer
    _global_analyzer = None
