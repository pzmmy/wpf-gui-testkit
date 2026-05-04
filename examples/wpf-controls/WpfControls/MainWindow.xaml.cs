using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Threading;

namespace WpfControls
{
    public partial class MainWindow : Window
    {
        private readonly DispatcherTimer _progressTimer = new();
        private bool _progressRunning;

        public MainWindow()
        {
            InitializeComponent();
            _progressTimer.Interval = TimeSpan.FromMilliseconds(100);
            _progressTimer.Tick += ProgressTimer_Tick;
        }

        private void Toggle_Checked(object sender, RoutedEventArgs e)
        {
            if (sender is ToggleButton btn && TxtToggleStatus != null)
            {
                string name = btn.Content?.ToString() ?? "?";
                TxtToggleStatus.Text = $"{name}: ON";
            }
        }

        private void Toggle_Unchecked(object sender, RoutedEventArgs e)
        {
            if (sender is ToggleButton btn && TxtToggleStatus != null)
            {
                string name = btn.Content?.ToString() ?? "?";
                TxtToggleStatus.Text = $"{name}: OFF";
            }
        }

        private void Radio_Checked(object sender, RoutedEventArgs e)
        {
            if (sender is RadioButton rb && TxtRadioStatus != null)
            {
                TxtRadioStatus.Text = $"Theme: {rb.Content}";
            }
        }

        private void Slider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (TxtSliderValue != null)
            {
                TxtSliderValue.Text = ((int)e.NewValue).ToString();
            }
        }

        private void Expander_StateChanged(object sender, RoutedEventArgs e)
        {
            if (sender is Expander exp && TxtExpanderStatus != null)
            {
                TxtExpanderStatus.Text = $"Expander: {(exp.IsExpanded ? "Expanded" : "Collapsed")}";
            }
        }

        private void DatePicker_Changed(object sender, SelectionChangedEventArgs e)
        {
            if (sender is DatePicker dp && TxtDateStatus != null)
            {
                TxtDateStatus.Text = dp.SelectedDate?.ToString("yyyy-MM-dd") ?? "No date selected";
            }
        }

        private void Progress_Start_Click(object sender, RoutedEventArgs e)
        {
            if (_progressRunning)
            {
                _progressTimer.Stop();
                _progressRunning = false;
            }
            else
            {
                _progressRunning = true;
                _progressTimer.Start();
            }
        }

        private void Progress_Reset_Click(object sender, RoutedEventArgs e)
        {
            _progressTimer.Stop();
            _progressRunning = false;
            ProgressBarDemo.Value = 0;
            TxtProgressStatus.Text = "0%";
        }

        private void ProgressTimer_Tick(object? sender, EventArgs e)
        {
            if (ProgressBarDemo.Value >= ProgressBarDemo.Maximum)
            {
                _progressTimer.Stop();
                _progressRunning = false;
                return;
            }
            ProgressBarDemo.Value += 2;
            TxtProgressStatus.Text = $"{(int)ProgressBarDemo.Value}%";
        }
    }
}
