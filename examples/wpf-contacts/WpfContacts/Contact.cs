using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace WpfContacts;

/// <summary>
/// 联系人数据模型。
/// </summary>
public class Contact : INotifyPropertyChanged
{
    private string _name = "";
    private string _phone = "";
    private string _email = "";
    private string _group = "朋友";

    public string Name
    {
        get => _name;
        set { _name = value; OnPropertyChanged(); }
    }

    public string Phone
    {
        get => _phone;
        set { _phone = value; OnPropertyChanged(); }
    }

    public string Email
    {
        get => _email;
        set { _email = value; OnPropertyChanged(); }
    }

    public string Group
    {
        get => _group;
        set { _group = value; OnPropertyChanged(); }
    }

    public string DisplayText => $"{Name} - {Phone}";

    public event PropertyChangedEventHandler? PropertyChanged;

    protected void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
