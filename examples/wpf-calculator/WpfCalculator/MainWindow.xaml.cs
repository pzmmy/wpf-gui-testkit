using System.Windows;
using System.Windows.Input;

namespace WpfCalculator
{
    public partial class MainWindow : Window
    {
        private double _currentValue = 0;
        private string _currentOperator = "";
        private bool _isNewEntry = true;
        private string _expression = "";

        public MainWindow()
        {
            InitializeComponent();
        }

        private void Number_Click(object sender, RoutedEventArgs e)
        {
            var btn = (System.Windows.Controls.Button)sender;
            string digit = btn.Content.ToString() ?? "";

            if (_isNewEntry)
            {
                DisplayText.Text = digit;
                _isNewEntry = false;
            }
            else
            {
                if (DisplayText.Text == "0")
                    DisplayText.Text = digit;
                else
                    DisplayText.Text += digit;
            }
        }

        private void Operator_Click(object sender, RoutedEventArgs e)
        {
            var btn = (System.Windows.Controls.Button)sender;
            string op = btn.Content.ToString() ?? "";

            if (double.TryParse(DisplayText.Text, out double val))
            {
                if (!string.IsNullOrEmpty(_currentOperator))
                {
                    Calculate();
                }
                else
                {
                    _currentValue = val;
                }
            }

            _currentOperator = op switch
            {
                "+" => "+",
                "-" => "-",
                "×" => "*",
                "÷" => "/",
                _ => _currentOperator
            };

            _expression = $"{_currentValue} {op} ";
            ExpressionText.Text = _expression;
            _isNewEntry = true;
        }

        private void Equals_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(_currentOperator))
            {
                Calculate();
                _currentOperator = "";
                ExpressionText.Text = "";
            }
        }

        private void Calculate()
        {
            if (!double.TryParse(DisplayText.Text, out double second)) return;

            double result = _currentOperator switch
            {
                "+" => _currentValue + second,
                "-" => _currentValue - second,
                "*" => _currentValue * second,
                "/" => second != 0 ? _currentValue / second : double.NaN,
                _ => second
            };

            DisplayText.Text = double.IsNaN(result) ? "错误" : result.ToString();
            _currentValue = result;
            _isNewEntry = true;
        }

        private void Clear_Click(object sender, RoutedEventArgs e)
        {
            DisplayText.Text = "0";
            _currentValue = 0;
            _currentOperator = "";
            _expression = "";
            ExpressionText.Text = "";
            _isNewEntry = true;
        }

        private void Decimal_Click(object sender, RoutedEventArgs e)
        {
            if (_isNewEntry)
            {
                DisplayText.Text = "0.";
                _isNewEntry = false;
            }
            else if (!DisplayText.Text.Contains("."))
            {
                DisplayText.Text += ".";
            }
        }

        private void Backspace_Click(object sender, RoutedEventArgs e)
        {
            if (_isNewEntry) return;
            if (DisplayText.Text.Length > 1)
                DisplayText.Text = DisplayText.Text[..^1];
            else
                DisplayText.Text = "0";
        }

        private void Negate_Click(object sender, RoutedEventArgs e)
        {
            if (DisplayText.Text == "0") return;
            if (DisplayText.Text.StartsWith("-"))
                DisplayText.Text = DisplayText.Text[1..];
            else
                DisplayText.Text = "-" + DisplayText.Text;
        }
    }
}
