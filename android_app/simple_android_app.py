from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        title = Label(text='Gold Scalper', font_size='28sp', bold=True)
        status = Label(text='Status: Running', font_size='20sp')
        symbol = Label(text='Symbol: XAUUSD', font_size='18sp')
        risk = Label(text='Risk: stop at entry', font_size='18sp')
        refresh = Button(text='Refresh')
        refresh.bind(on_press=self.refresh_status)

        layout.add_widget(title)
        layout.add_widget(status)
        layout.add_widget(symbol)
        layout.add_widget(risk)
        layout.add_widget(refresh)
        self.add_widget(layout)

    def refresh_status(self, instance):
        self.children[0].children[1].text = 'Status: Updated'


class GoldScalperApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    GoldScalperApp().run()
