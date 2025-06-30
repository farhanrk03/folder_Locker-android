
import os, json, shutil, pyzipper
from plyer import filechooser
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import mainthread
from kivy.metrics import dp

HISTORY_FILE = "history.json"

def show_popup(msg):
    Popup(title="Info", content=Label(text=msg), size_hint=(0.8, 0.3)).open()

class EyeToggle(ButtonBehavior, Image):
    def __init__(self, textinput, **kwargs):
        super().__init__(**kwargs)
        self.ti = textinput
        self.source = "assets/eye_closed.png"
        self.update_icon()
    def on_press(self):
        self.ti.password = not self.ti.password
        self.update_icon()
    def update_icon(self):
        self.source = "assets/eye_open.png" if not self.ti.password else "assets/eye_closed.png"

def ask_password(callback):
    layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    layout.bind(minimum_height=layout.setter('height'))

    pw_input = TextInput(
        hint_text="Enter Password",
        password=True,
        multiline=False,
        size_hint_y=None,
        height=dp(40),
        padding=[dp(10), dp(10)],
        halign='center'
    )

    eye = EyeToggle(pw_input)
    eye.size_hint = (None, None)
    eye.size = dp(30), dp(30)

    row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
    row.add_widget(pw_input)
    row.add_widget(eye)

    layout.add_widget(row)

  
    btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
    ok_btn = Button(text="OK")
    cancel_btn = Button(text="X", size_hint_x=None, width=dp(40))
    btn_row.add_widget(ok_btn)
    btn_row.add_widget(cancel_btn)
    layout.add_widget(btn_row)

    popup = Popup(
        title="Enter Password",
        content=layout,
        size_hint=(None, None),
        size=(dp(300), dp(180)),
        auto_dismiss=False
    )

    ok_btn.bind(on_press=lambda x: (popup.dismiss(), callback(pw_input.text)) if pw_input.text else None)
    cancel_btn.bind(on_press=popup.dismiss)

    popup.open()
    
    def validate_password(instance):
        password = pw_input.text.strip()
        if len(password) < 8:
            show_popup("Password must be at least 8 characters.")
        else:
            popup.dismiss()
            callback(password)

    ok_btn.bind(on_press=validate_password)
    cancel_btn.bind(on_press=popup.dismiss)

    popup.open()

def ask_old_new_password(callback):
    layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    layout.bind(minimum_height=layout.setter('height'))

    old = TextInput(
        hint_text="Old Password",
        password=True,
        multiline=False,
        padding=[dp(10), dp(10)],
        halign='center',
        size_hint_y=None,
        height=dp(40)
    )

    new = TextInput(
        hint_text="New Password",
        password=True,
        multiline=False,
        padding=[dp(10), dp(10)],
        halign='center',
        size_hint_y=None,
        height=dp(40)
    )

    eye1 = EyeToggle(old)
    eye2 = EyeToggle(new)
    eye1.size_hint = eye2.size_hint = (None, None)
    eye1.size = eye2.size = dp(30), dp(30)

    b1 = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
    b2 = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
    b1.add_widget(old); b1.add_widget(eye1)
    b2.add_widget(new); b2.add_widget(eye2)

    layout.add_widget(b1)
    layout.add_widget(b2)

    # Tombol OK dan Cancel
    btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
    ok_btn = Button(text="OK")
    cancel_btn = Button(text="X", size_hint_x=None, width=dp(40))
    btn_row.add_widget(ok_btn)
    btn_row.add_widget(cancel_btn)
    layout.add_widget(btn_row)

    popup = Popup(
        title="Change Password",
        content=layout,
        size_hint=(None, None),
        size=(dp(300), dp(230)),
        auto_dismiss=False
    )

    def validate_change_password(instance):
        old_pw = old.text.strip()
        new_pw = new.text.strip()
        if not old_pw:
            show_popup("Old password cannot be empty.")
        elif len(new_pw) < 8:
            show_popup("New password must be at least 8 characters.")
        elif old_pw == new_pw:
            show_popup("New password must be different from old password.")
        else:
            popup.dismiss()
            callback(old_pw, new_pw)

    ok_btn.bind(on_press=validate_change_password)
    cancel_btn.bind(on_press=popup.dismiss)

    popup.open()

    
def save_history(folder):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    if folder not in history:
        history.append(folder)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)

@mainthread
def lock_folder(password):
    folder = filechooser.choose_dir(title="Select Folder")
    if not folder:
        return
    folder = folder[0]
    zip_path = folder + ".zip"
    try:
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED,
                                 encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(password.encode())
            for root, _, files in os.walk(folder):
                for f in files:
                    path = os.path.join(root, f)
                    arc = os.path.relpath(path, folder)
                    zf.write(path, arc)
        shutil.rmtree(folder)
        save_history(folder)
        show_popup("Folder locked successfully.")
    except Exception as e:
        show_popup("Failed to lock: " + str(e))

@mainthread
def unlock_folder(password):
    zip_file = filechooser.open_file(filters=[("*.zip", "*.zip")])
    if not zip_file:
        return
    zip_file = zip_file[0]
    try:
        with pyzipper.AESZipFile(zip_file) as zf:
            zf.setpassword(password.encode())
            extract_path = zip_file.replace(".zip", "")
            zf.extractall(extract_path)
        os.remove(zip_file)
        show_popup("Folder unlocked successfully.")
    except Exception as e:
        show_popup("Failed to unlock: " + str(e))

@mainthread
def change_zip_password(old, new):
    zip_file = filechooser.open_file(filters=[("*.zip", "*.zip")])
    if not zip_file:
        return
    zip_file = zip_file[0]
    temp_dir = zip_file.replace(".zip", "_temp")
    try:
        with pyzipper.AESZipFile(zip_file, 'r') as zf:
            zf.setpassword(old.encode())
            zf.extractall(temp_dir)
        with pyzipper.AESZipFile(zip_file, 'w', compression=pyzipper.ZIP_DEFLATED,
                                 encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(new.encode())
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    path = os.path.join(root, f)
                    arc = os.path.relpath(path, temp_dir)
                    zf.write(path, arc)
        shutil.rmtree(temp_dir)
        show_popup("Password changed successfully.")
    except Exception as e:
        show_popup("Failed to change password: " + str(e))

@mainthread
def show_history():
    if not os.path.exists(HISTORY_FILE):
        show_popup("No history found.")
        return
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    show_popup("\n".join(history))
