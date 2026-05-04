using System.Windows;

namespace WpfContacts;

/// <summary>
/// 新增/编辑联系人的对话框窗口。
/// </summary>
public partial class ContactDialog : Window
{
    public ContactDialog(Contact? existing)
    {
        InitializeComponent();

        // 编辑时预填数据
        if (existing != null)
        {
            Title = "编辑联系人";
            this.DataContext = new Contact
            {
                Name = existing.Name,
                Phone = existing.Phone,
                Email = existing.Email,
                Group = existing.Group,
            };
        }
        else
        {
            Title = "新增联系人";
            this.DataContext = new Contact();
        }
    }

    /// <summary>对话框返回的联系人数据。</summary>
    public Contact? Result => DialogResult == true ? (DataContext as Contact) : null;

    private void OnSaveClick(object sender, RoutedEventArgs e)
    {
        var contact = DataContext as Contact;
        if (contact == null) { DialogResult = false; return; }

        // 简单校验：姓名和电话必填
        if (string.IsNullOrWhiteSpace(contact.Name))
        {
            MessageBox.Show("请输入姓名。", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            TxtName.Focus();
            return;
        }
        if (string.IsNullOrWhiteSpace(contact.Phone))
        {
            MessageBox.Show("请输入电话。", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            TxtPhone.Focus();
            return;
        }

        DialogResult = true;
    }
}
