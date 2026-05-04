using System.Windows;
using System.Windows.Threading;

namespace WpfContacts;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();

        if (DataContext is MainViewModel vm)
        {
            // 注入对话框回调
            vm.ShowContactDialog = contact =>
            {
                var dialog = new ContactDialog(contact);
                return dialog.ShowDialog() == true ? dialog.Result : null;
            };

            // 注入消息提示
            vm.ShowMessage = msg =>
            {
                Dispatcher.BeginInvoke(() =>
                {
                    TxtMessage.Text = msg;
                    // 3 秒后自动清除
                    var timer = new DispatcherTimer
                    {
                        Interval = TimeSpan.FromSeconds(3)
                    };
                    timer.Tick += (s, e) =>
                    {
                        TxtMessage.Text = "";
                        timer.Stop();
                    };
                    timer.Start();
                });
            };
        }
    }
}
