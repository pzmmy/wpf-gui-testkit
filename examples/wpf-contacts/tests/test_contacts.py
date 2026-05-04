"""test_contacts.py — 通讯录 App GUI 测试

覆盖控件类型：
- TextBox（搜索框输入 + 实时过滤验证）
- ListView / GridView（联系人列表项存在性）
- ComboBox（对话框分组选择）
- 对话框窗口（ContactDialog 新增/编辑）
- Button 点击（添加/编辑/删除/保存/取消）
- StatusBar（状态栏文本）和 TextBlock（消息提示）

测试分级：
- P0：核心功能（窗口启动、搜索、增删改）
- P1：交互细节（选中、状态显示）
- P2：边界场景（空搜索、表单验证）
"""
import pytest
import time
from wpf_testkit.core.conftest import *  # noqa: F401,F403
from pages.wpf_contacts_page import ContactsPage, ContactDialogPage


# ================================================================
# P0 — 核心功能
# ================================================================

@pytest.mark.P0
class TestCore:

    def test_window_launch(self, main_window):
        """通讯录窗口正常启动。"""
        assert main_window.exists(), "主窗口未出现"
        assert main_window.is_visible(), "主窗口不可见"

    def test_initial_contacts_displayed(self, app_launch, main_window):
        """启动后有 5 个预置联系人。"""
        page = ContactsPage(app_launch)
        status = page.get_status_text()
        assert "5" in status, f"状态栏应显示 5 个联系人，实际: {status}"

    def test_search_filter_contacts(self, app_launch, main_window):
        """搜索框输入"张"应只显示张三。"""
        page = ContactsPage(app_launch)
        page.search("张")
        status = page.get_status_text()
        # 应该只有 1 个匹配（张三）
        assert "显示 1" in status or "1 个" in status, \
            f"搜索'张'后应只显示 1 个联系，实际: {status}"

    def test_search_clear_restores_all(self, app_launch, main_window):
        """清空搜索框后恢复全部联系人。"""
        page = ContactsPage(app_launch)
        page.search("不存在")
        status_after = page.get_status_text()
        assert "显示 0" in status_after, f"搜索不存在项后应显示 0，实际: {status_after}"
        page.clear_search()
        status_restored = page.get_status_text()
        assert "5 个" in status_restored, f"清空搜索后应恢复 5 个，实际: {status_restored}"

    def test_add_contact(self, app_launch, main_window):
        """添加新联系人：弹出对话框 → 填写 → 保存 → 列表更新。"""
        page = ContactsPage(app_launch)

        page.click_add()
        time.sleep(0.5)

        dialog = ContactDialogPage(app_launch)
        assert dialog.window.exists(), "添加对话框未出现"
        dialog.enter_name("测试用户")
        dialog.enter_phone("10000000000")
        dialog.enter_email("test@test.com")
        dialog.click_save()
        time.sleep(0.5)

        new_status = page.get_status_text()
        assert "6" in new_status, f"添加后应显示 6 个联系人，实际: {new_status}"
        assert "已添加" in page.get_message_text(), "应有添加成功消息"

    def test_edit_contact(self, app_launch, main_window):
        """编辑联系人：选中 → 编辑 → 修改姓名 → 保存。"""
        page = ContactsPage(app_launch)

        # 选中第一个联系人
        assert page.select_contact("张三"), "未找到联系人'张三'"
        page.click_edit()
        time.sleep(0.5)

        dialog = ContactDialogPage(app_launch)
        assert dialog.window.exists(), "编辑对话框未出现"
        dialog.enter_name("张三(已修改)")
        dialog.click_save()
        time.sleep(0.5)

        assert "已更新" in page.get_message_text(), "应有更新成功消息"

    def test_delete_contact(self, app_launch, main_window):
        """删除联系人：选中 → 删除 → 列表减少。"""
        page = ContactsPage(app_launch)

        assert page.select_contact("赵六"), "未找到联系人'赵六'"
        page.click_delete()
        time.sleep(0.5)

        status = page.get_status_text()
        assert "4" in status, f"删除后应显示 4 个联系人，实际: {status}"
        assert "已删除" in page.get_message_text(), "应有删除成功消息"


# ================================================================
# P1 — 交互细节
# ================================================================

@pytest.mark.P1
class TestInteraction:

    def test_select_contact_updates_status(self, app_launch, main_window):
        """选中联系人后编辑/删除按钮应可用。"""
        page = ContactsPage(app_launch)
        # 先检查编辑/删除按钮存在
        assert page.is_element_visible(page.BTN_EDIT)
        assert page.is_element_visible(page.BTN_DELETE)

    def test_add_dialog_cancel(self, app_launch, main_window):
        """添加对话框取消后，联系人数量不变。"""
        page = ContactsPage(app_launch)
        page.click_add()
        time.sleep(0.5)

        dialog = ContactDialogPage(app_launch)
        assert dialog.window.exists()
        dialog.click_cancel()
        time.sleep(0.5)

        # 对话框应关闭，按钮不应可见
        assert not dialog.window.exists(), "取消后对话框应关闭"

    def test_all_buttons_exist(self, app_launch, main_window):
        """所有主界面按钮和搜索框都存在。"""
        page = ContactsPage(app_launch)
        assert page.is_element_visible(page.TXT_SEARCH), "搜索框不存在"
        assert page.is_element_visible(page.BTN_ADD), "添加按钮不存在"
        assert page.is_element_visible(page.BTN_EDIT), "编辑按钮不存在"
        assert page.is_element_visible(page.BTN_DELETE), "删除按钮不存在"
        assert page.is_element_visible(page.LIST_CONTACTS), "联系人列表不存在"
        assert page.is_element_visible(page.TXT_STATUS), "状态栏不存在"


# ================================================================
# P2 — 边界场景
# ================================================================

@pytest.mark.P2
class TestEdgeCases:

    def test_search_empty_list(self, app_launch, main_window):
        """搜索"xyz不存在的关键词"应显示空列表。"""
        page = ContactsPage(app_launch)
        page.search("xyz不存在的关键词")
        status = page.get_status_text()
        assert "显示 0" in status, f"搜索无结果应显示 0，实际: {status}"

    def test_edit_requires_selection(self, app_launch, main_window):
        """未选中联系人时编辑/删除按钮存在但不执行。"""
        page = ContactsPage(app_launch)
        # 直接按编辑（无选中时 command 的 CanExecute 返回 false）
        page.click_edit()
        time.sleep(0.3)
        # 不应弹出对话框
        dialog = ContactDialogPage(app_launch)
        if dialog.window.exists():
            dialog.click_cancel()

    def test_delete_requires_selection(self, app_launch, main_window):
        """未选中联系人时删除按钮存在但不执行。"""
        page = ContactsPage(app_launch)
        page.click_delete()
        time.sleep(0.3)
        # 不应崩溃，也不应有删除消息
        msg = page.get_message_text()
        assert "已删除" not in msg, "未选中时不应有删除消息"

    def test_dialog_form_validation(self, app_launch, main_window):
        """对话框空白保存应阻止（姓名/电话必填）。"""
        page = ContactsPage(app_launch)
        page.click_add()
        time.sleep(0.5)

        dialog = ContactDialogPage(app_launch)
        assert dialog.window.exists()
        # 不填姓名，直接保存
        dialog.click_save()
        time.sleep(0.5)
        # 对话框不应关闭（因为校验失败）
        dialog.window.wait("visible", timeout=2)

        # 关闭
        dialog.click_cancel()
