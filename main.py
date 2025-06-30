from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from lockutils import *
from kivy.clock import Clock

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_main, 2)

    def switch_to_main(self, dt):
        self.manager.current = 'main'

class MainMenu(Screen):
    def lock_folder(self):
        ask_password(callback=lock_folder)
    def unlock_folder(self):
        ask_password(callback=unlock_folder)
    def change_pw(self):
        ask_old_new_password(callback=change_zip_password)
    def show_history(self):
        show_history()

class FolderLockerApp(App):
    def build(self):
        Builder.load_file("ui_with_animated.kv")
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainMenu(name="main"))
        return sm

if __name__ == '__main__':
    FolderLockerApp().run()
