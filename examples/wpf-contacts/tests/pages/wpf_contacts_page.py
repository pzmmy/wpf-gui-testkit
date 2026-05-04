"""wpf_contacts_page.py — 通讯录 App Page Object

覆盖控件类型：
- TextBox（搜索框、表单输入）
- ListView / GridView（联系人列表）
- ComboBox（分组选择）
- Button（添加/编辑/删除/保存/取消）
- StatusBar / TextBlock（状态栏、消息提示）
- 子窗口（ContactDialog 对话框）
"""
from wpf_testkit.core.base_page import BasePage


class ContactsPage(BasePage):
    """通讯录主界面 Page Object。"""

    # ── AutomationId 常量 ──────────────────────────────────
    TXT_SEARCH = "TxtSearch"
    LIST_CONTACTS = "ListContacts"
    BTN_ADD = "BtnAdd"
    BTN_EDIT = "BtnEdit"
    BTN_DELETE = "BtnDelete"
    TXT_STATUS = "TxtStatus"
    TXT_MESSAGE = "TxtMessage"

    @property
    def window(self):
        if self._window is None:
            self._window = self.app.window(auto_id="MainWindow")
        return self._window

    # ── 搜索 ────────────────────────────────────────────────

    def search(self, keyword: str):
        """在搜索框输入关键词，实时过滤联系人。"""
        self.set_text(self.TXT_SEARCH, keyword)

    def clear_search(self):
        """清空搜索框。"""
        self.set_text(self.TXT_SEARCH, "")

    # ── 列表操作 ────────────────────────────────────────────

    def get_contact_count(self) -> int:
        """获取当前显示的联系人数量。"""
        lst = self.window.child_window(auto_id=self.LIST_CONTACTS)
        if not lst.exists():
            return 0
        return len(lst.descendants())

    def select_contact(self, name: str):
        """按姓名选中联系人。"""
        lst = self.window.child_window(auto_id=self.LIST_CONTACTS)
        lst.wait("enabled", timeout=5)
        for item in lst.descendants():
            try:
                if name in item.window_text():
                    item.click_input()
                    return True
            except Exception:
                continue
        return False

    def get_first_contact_name(self) -> str:
        """获取列表第一项的联系人姓名（通过 GridView 列）。"""
        lst = self.window.child_window(auto_id=self.LIST_CONTACTS)
        if not lst.exists():
            return ""
        items = lst.descendants()
        if not items:
            return ""
        return items[0].window_text()

    # ── 按钮操作 ────────────────────────────────────────────

    def click_add(self):
        """点击添加按钮。"""
        self.click_element(self.BTN_ADD)

    def click_edit(self):
        """点击编辑按钮。"""
        self.click_element(self.BTN_EDIT)

    def click_delete(self):
        """点击删除按钮。"""
        self.click_element(self.BTN_DELETE)

    # ── 状态查询 ────────────────────────────────────────────

    def get_status_text(self) -> str:
        """获取状态栏文本。"""
        return self.get_text(self.TXT_STATUS)

    def get_message_text(self) -> str:
        """获取消息文本。"""
        return self.get_text(self.TXT_MESSAGE)


class ContactDialogPage(BasePage):
    """新增/编辑联系人的对话框 Page Object。"""

    TXT_NAME = "TxtName"
    TXT_PHONE = "TxtPhone"
    TXT_EMAIL = "TxtEmail"
    COMBO_GROUP = "ComboGroup"
    BTN_SAVE = "BtnSave"
    BTN_CANCEL = "BtnCancel"

    @property
    def window(self):
        # 对话框窗口通过 auto_id 定位
        if self._window is None:
            self._window = self.app.window(auto_id="ContactDialog")
        return self._window

    def enter_name(self, name: str):
        self.set_text(self.TXT_NAME, name)

    def enter_phone(self, phone: str):
        self.set_text(self.TXT_PHONE, phone)

    def enter_email(self, email: str):
        self.set_text(self.TXT_EMAIL, email)

    def select_group(self, group: str):
        """选择分组（通过键盘操作 ComboBox）。"""
        combo = self.window.child_window(auto_id=self.COMBO_GROUP)
        combo.wait("enabled", timeout=5)
        combo.set_focus()
        combo.type_keys("%{DOWN}")
        # 搜索目标项
        for item in combo.descendants():
            try:
                if group in item.window_text():
                    item.click_input()
                    return
            except Exception:
                continue
        combo.type_keys("{ENTER}")

    def click_save(self):
        self.click_element(self.BTN_SAVE)

    def click_cancel(self):
        self.click_element(self.BTN_CANCEL)

    def get_name_text(self) -> str:
        return self.get_text(self.TXT_NAME)

    def get_phone_text(self) -> str:
        return self.get_text(self.TXT_PHONE)
