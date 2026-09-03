from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json


class GoldScalperLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=16, spacing=12, **kwargs)

        # Title
        title = Label(text='[b]Gold Scalper MT5[/b]', markup=True, halign='center', font_size='28sp')
        self.add_widget(title)

        # Config section
        config_layout = GridLayout(cols=2, size_hint_y=0.25, spacing=12)
        config_layout.add_widget(Label(text='Server IP:', font_size='14sp'))
        self.ip_input = TextInput(text='192.168.1.100', multiline=False, size_hint_x=0.6)
        config_layout.add_widget(self.ip_input)
        config_layout.add_widget(Label(text='Port:', font_size='14sp'))
        self.port_input = TextInput(text='5000', multiline=False, size_hint_x=0.6)
        config_layout.add_widget(self.port_input)
        self.add_widget(config_layout)

        # Status cards
        self.status_label = Label(text='Status: CONNECTING...', halign='center', font_size='22sp', bold=True, color=(0.4, 1, 0.6, 1))
        self.add_widget(self.status_label)

        self.symbol_label = Label(text='Symbol: ---', font_size='18sp')
        self.add_widget(self.symbol_label)

        self.signal_label = Label(text='Signal: WAIT', font_size='18sp', color=(1, 1, 0.4, 1))
        self.add_widget(self.signal_label)

        self.balance_label = Label(text='Balance: $0.00', font_size='18sp', color=(0.4, 1, 0.6, 1))
        self.add_widget(self.balance_label)

        self.pnl_label = Label(text='P/L: $0.00', font_size='18sp', color=(1, 0.4, 0.4, 1))
        self.add_widget(self.pnl_label)

        self.positions_label = Label(text='Open: 0', font_size='18sp')
        self.add_widget(self.positions_label)

        # Buttons
        button_layout = BoxLayout(size_hint_y=0.2, spacing=12)
        refresh_btn = Button(text='Refresh')
        refresh_btn.bind(on_press=self.refresh_status)
        button_layout.add_widget(refresh_btn)

        admin_btn = Button(text='Admin Panel')
        admin_btn.bind(on_press=self.open_admin)
        button_layout.add_widget(admin_btn)

        self.add_widget(button_layout)

        # Start auto-refresh
        Clock.schedule_interval(self.refresh_status, 5)

    def get_url(self):
        ip = self.ip_input.text or '192.168.1.100'
        port = self.port_input.text or '5000'
        return f'http://{ip}:{port}/status'

    def refresh_status(self, *args):
        try:
            url = self.get_url()
            UrlRequest(url, on_success=self.on_status_success, on_failure=self.on_status_failure)
        except Exception:
            self.status_label.text = 'Status: CONNECTION ERROR'

    def on_status_success(self, request, data):
        try:
            info = json.loads(data)
            self.status_label.text = f"Status: {info.get('status', 'UNKNOWN').upper()}"
            self.symbol_label.text = f"Symbol: {info.get('symbol', 'XAUUSD')}"
            self.signal_label.text = f"Signal: {info.get('last_signal', 'WAIT')}"
            balance = info.get('account_balance', 0.0)
            self.balance_label.text = f"Balance: ${balance:,.2f}"
            pnl = info.get('floating_pnl', 0.0)
            self.pnl_label.text = f"P/L: ${pnl:,.2f}"
            positions = info.get('positions_count', 0)
            self.positions_label.text = f"Open: {positions}"
        except Exception:
            self.status_label.text = 'Status: PARSE ERROR'

    def on_status_failure(self, request, value):
        self.status_label.text = 'Status: OFFLINE'

    def open_admin(self, instance):
        import webbrowser
        ip = self.ip_input.text or '192.168.1.100'
        webbrowser.open(f'http://{ip}:5050/')


class GoldScalperApp(App):
    def build(self):
        self.title = 'Gold Scalper'
        return GoldScalperLayout()


if __name__ == '__main__':
    GoldScalperApp().run()

