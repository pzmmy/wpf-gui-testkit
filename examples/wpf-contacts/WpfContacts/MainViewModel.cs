using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Input;

namespace WpfContacts;

/// <summary>
/// 通讯录主界面的 ViewModel。
/// </summary>
public class MainViewModel : INotifyPropertyChanged
{
    private readonly ObservableCollection<Contact> _allContacts = new();
    private string _searchText = "";
    private Contact? _selectedContact;

    public MainViewModel()
    {
        // 预置 5 个示例联系人
        _allContacts.Add(new Contact { Name = "张三", Phone = "13800138001", Email = "zhangsan@example.com", Group = "家人" });
        _allContacts.Add(new Contact { Name = "李四", Phone = "13900139002", Email = "lisi@example.com", Group = "朋友" });
        _allContacts.Add(new Contact { Name = "王五", Phone = "13700137003", Email = "wangwu@example.com", Group = "同事" });
        _allContacts.Add(new Contact { Name = "赵六", Phone = "13600136004", Email = "zhaoliu@example.com", Group = "朋友" });
        _allContacts.Add(new Contact { Name = "孙七", Phone = "13500135005", Email = "sunqi@example.com", Group = "家人" });
        RefreshFilteredList();

        AddContactCommand = new RelayCommand(_ => OpenAddDialog());
        EditContactCommand = new RelayCommand(_ => OpenEditDialog(), _ => SelectedContact != null);
        DeleteContactCommand = new RelayCommand(_ => DeleteContact(), _ => SelectedContact != null);
    }

    /// <summary>搜索文本，实时过滤联系人列表。</summary>
    public string SearchText
    {
        get => _searchText;
        set
        {
            _searchText = value;
            OnPropertyChanged();
            RefreshFilteredList();
        }
    }

    /// <summary>过滤后的联系人列表（绑定到 ListView）。</summary>
    public ObservableCollection<Contact> Contacts { get; } = new();

    /// <summary>当前选中的联系人。</summary>
    public Contact? SelectedContact
    {
        get => _selectedContact;
        set
        {
            _selectedContact = value;
            OnPropertyChanged();
            CommandManager.InvalidateRequerySuggested();
        }
    }

    /// <summary>状态栏文本。</summary>
    public string StatusText => $"共 {_allContacts.Count} 个联系人，显示 {Contacts.Count} 个";

    public ICommand AddContactCommand { get; }
    public ICommand EditContactCommand { get; }
    public ICommand DeleteContactCommand { get; }

    /// <summary>外部可注入的打开对话框回调。返回新联系人信息，或 null 表示取消。</summary>
    public Func<Contact?, Contact?>? ShowContactDialog { get; set; }

    /// <summary>外部可注入的消息提示回调。</summary>
    public Action<string>? ShowMessage { get; set; }

    private void RefreshFilteredList()
    {
        Contacts.Clear();
        var filtered = string.IsNullOrWhiteSpace(_searchText)
            ? _allContacts
            : new ObservableCollection<Contact>(
                _allContacts.Where(c =>
                    c.Name.Contains(_searchText, StringComparison.OrdinalIgnoreCase) ||
                    c.Phone.Contains(_searchText) ||
                    c.Email.Contains(_searchText, StringComparison.OrdinalIgnoreCase) ||
                    c.Group.Contains(_searchText, StringComparison.OrdinalIgnoreCase)));

        foreach (var c in filtered)
            Contacts.Add(c);

        OnPropertyChanged(nameof(StatusText));
    }

    private void OpenAddDialog()
    {
        if (ShowContactDialog == null) return;
        var newContact = ShowContactDialog.Invoke(null);
        if (newContact == null) return;
        _allContacts.Add(newContact);
        RefreshFilteredList();
        ShowMessage?.Invoke($"已添加联系人：{newContact.Name}");
    }

    private void OpenEditDialog()
    {
        if (ShowContactDialog == null || SelectedContact == null) return;
        var updated = ShowContactDialog.Invoke(SelectedContact);
        if (updated == null) return;
        // 更新选中联系人的字段
        var idx = _allContacts.IndexOf(SelectedContact);
        if (idx >= 0)
        {
            _allContacts[idx] = updated;
        }
        RefreshFilteredList();
        ShowMessage?.Invoke($"已更新联系人：{updated.Name}");
    }

    private void DeleteContact()
    {
        if (SelectedContact == null) return;
        var name = SelectedContact.Name;
        _allContacts.Remove(SelectedContact);
        SelectedContact = null;
        RefreshFilteredList();
        ShowMessage?.Invoke($"已删除联系人：{name}");
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    protected void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// 简化版的 RelayCommand。
/// </summary>
public class RelayCommand : ICommand
{
    private readonly Action<object?> _execute;
    private readonly Func<object?, bool>? _canExecute;

    public RelayCommand(Action<object?> execute, Func<object?, bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }

    public bool CanExecute(object? parameter) => _canExecute?.Invoke(parameter) ?? true;
    public void Execute(object? parameter) => _execute(parameter);
}
