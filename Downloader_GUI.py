from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from os.path import sep, expanduser, isdir, dirname, join
from kivy.garden.filebrowser import FileBrowser
from kivy.properties import BooleanProperty
from kivy.utils import platform
from kivy.uix.gridlayout import GridLayout
from multiprocessing import Pipe, Process
from kivy.clock import Clock
from pySmartDL import SmartDL
import webbrowser
import mechanize
import subprocess
import time
import json
import ctypes
import os


def encrypter(msg_text, secret_key):
    ''' encrypter will encrypt any text into integer using your secret_key'''
    n = len(msg_text)
    temp = []
    temp2 = []
    encrypted = ''
    # encryption
    encrypted_1 = msg_text[int(secret_key[1]):] + msg_text[:int(secret_key[1])]
    for a in encrypted_1:
        temp.append(chr(ord(a) + int(secret_key[0])))
    encrypted_2 = temp[int(secret_key[2]):] + temp[:int(secret_key[2])]
    temp2.append(str(ord(encrypted_2[0])))
    for i in range(1, n):
        temp2.append(str(ord(encrypted_2[i]) + int(temp2[i-1])))
    for i in range(n):
        temp2[i] = temp2[i].zfill(len(temp2[n-1]))
        encrypted = encrypted + ''.join(temp2[i])
    encrypted = encrypted + str(len(temp2[n-1]))
    return encrypted


def decrypter(encrypted_text, secret_key):
    ''' decrypter will decrypt encrypted text of encrypt function'''
    temp3 = []
    temp2 = []
    temp1 = ''
    m = len(encrypted_text)
    key = int(encrypted_text[m - 1])
    n = m//key
    i = 0
    j = key
    # decryption
    for a in range(n):
        temp2.append(encrypted_text[i:j])
        i = i + key
        j = j + key
    temp3.append(chr(int(temp2[0])))
    for i in range(1, n):
        temp3.append(chr(int(temp2[i]) - int(temp2[i-1])))
    decrypted_2 = temp3[n - int(secret_key[2]):] + \
        temp3[:n - int(secret_key[2])]

    for a in decrypted_2:
        temp1 = temp1 + ''.join(chr(ord(a) - int(secret_key[0])))
    decrypted_1 = temp1[n - int(secret_key[1]):] + \
        temp1[:n - int(secret_key[1])]
    return decrypted_1


def main(conn, select, download, path, username=None, password=None):

    br = mechanize.Browser()

    def downloader(download, p):
        filetypes = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png",
                     ".ppt", ".pptx", ".zip", ".rar", ".txt", ".rtf", ".mp3",
                     ".mp4", ".webm", ".ogg", ".3gp", ".avi", ".mov", ".gif",
                     ".7z", ".c", ".cpp", ".py", ".java", ".epub", ".sh",
                     ".exe", ".tar", ".mkv", ".psd", ".bmp", ]
        try:
            print(download)
            br.open(download)
        except Exception as e:
            print(e)
            conn.send("error"+str(e)+"\n")
            return
        myfiles = []
        mydir = []
        for link in br.links():
            for type in filetypes:
                if type in link.text.lower():
                    myfiles.append(link)
            if(link.text):
                if link.text[-1] == "/":
                    if link.text[-2] != '.':
                        mydir.append(link)
        for link in myfiles:
            downloadlink(link, p)
        for link in mydir:
            n = len(link.text)
            try:
                subprocess.check_output("mkdir " + '''\"{}'''.format(p) +
                                        '\\' +
                                        '''{}\"'''.format(link.text[:n-1]),
                                        shell=True)
            except Exception:
                pass
            downloader(link.absolute_url,
                       p + '\\' + link.text[:n-1])
        return

    def c_downloader(download, p):
        print(download)
        try:
            print("wtf")
            br.open(download)
        except Exception as e:
            print(e)
            conn.send("error"+str(e)+"\n")
            # return
        for link in br.links():
            if ".pdf" in link.text.lower():
                print(link.text)
                downloadlink(link, p, False, True)
            elif " File" in link.text:
                downloadlink(link, p, False, False)

    def downloadlink(l, po, select=True, file=None):
        if not l.text:
            return
        if not select:
            if file:
                if po[-1] == '\\':
                    f = open(po + l.text, "wb")
                else:
                    f = open(po + '\\' + l.text, "wb")
            else:
                n = len(l.text)
                f = open(po + '\\' + l.text[:n-5] + ".pdf", "wb")
        try:
            if not select:
                br.open(l.absolute_url)
                f.write(br.response().read())
                print(l.text + " downloaded")
                conn.send(l.text + " downloaded\n")
            else:
                print(l.text)
                conn.send(l.text + "\n")
                obj = SmartDL(l.absolute_url, po, progress_bar=False)
                obj.start(blocking=False)
                conn.send("new")
                while not obj.isFinished():
                    # complete = False
                    speed = obj.get_speed(human=True)
                    dl_size = obj.get_dl_size(human=True)
                    total_size = obj.get_final_filesize(human=True)
                    eta = obj.get_eta(human=True)
                    progress = obj.get_progress_bar(length=20)
                    d_state = "[*] {0}//{1} @ {2} {3}   ETA: {4}\n".format(dl_size,
                                                                           total_size,
                                                                           speed,
                                                                           progress,
                                                                           eta)
                    conn.send(d_state)
                    time.sleep(0.2)

                if obj.isSuccessful():
                    conn.send("finish")
                    dl_time = obj.get_dl_time(human=False)
                    conn.send(
                        l.text + " downloaded successfully in {}s\n".format(dl_time))
                else:
                    conn.send("finish")
                    print("There were some errors:")
                    conn.send("There were some errors:\n")
                    for e in obj.get_errors():
                        print(str(e))
                        conn.send(str(e)+"\n")
                conn.send("\n\n\n")
                return
        except Exception as e:
            print(e)
            conn.send("error"+str(e)+"\n")
            return

    print("Mass download files and folders from Intranet and Courses")
    print("Note: if you enter wrong password for courses it won't download.")
    print("Note: To reset password delete 'pass.json' file.")
    print("Note: it won't download embedded PDF file of courses.")

    if select == 'c':
        br.open("https://courses.daiict.ac.in/login/index.php")
        br.select_form(nr=0)
        br.form['username'] = username
        br.form['password'] = password
        br.submit()
        print("you have succesfully login into your account.")
        conn.send("you have succesfully login into your account.\n")

    print("please wait if you don't see any error it's downloading.")
    conn.send("please wait if you don't see any error it's downloading.\n")

    t1 = time.perf_counter()
    if select != 'c':
        print("hi")
        downloader(download, path)
    else:
        print("c hi")
        print(download)
        c_downloader(download, path)
    t2 = time.perf_counter()

    print("{}".format(round(t2-t1, 2)))
    conn.send("end")
    # conn.send("end")
    # print("Created by ALPHA")
    return


Builder.load_string('''
<Widgets>:
    rows: 4
    spacing: 10
    padding: 8
    set_path: path
    set_link: link
    set_select: toggle_button
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        spacing: 5
        size_hint: (1,0.20)
        Button:
            text: "Login"
            on_release: root.show_login()
            size_hint: (0.32,1)
            pos_hint: ({'left':1,'top':1})
            font_size: (root.width**2 + root.height**2) / 14**4
        ToggleButton:
            id: toggle_button
            size_hint: (0.32,1)
            text: "Intranet"
            font_size: (root.width**2 + root.height**2) / 14**4
            on_state:
                if self.state == 'normal': root.intranet()
                else: root.courses()
        Button:
            text: "Help"
            on_release: root.show_help()
            size_hint: (0.32, 1)
            font_size: (root.width**2 + root.height**2) / 14**4
        Label:
            text: ''
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        spacing: 5
        size_hint: (1,0.20)
        Label:
            text: 'Link:'
            size_hint:(0.32,1)
            pos_hint: ({'x':self.x,'top':1})
            font_size: (root.width**2 + root.height**2) / 14**4
        TextInput:
            id: link
            multiline: False
            font_size: (root.width**2 + root.height**2) / 14**4
            size_hint: (0.72,1)
            pos_hint: ({'x':self.x,'top':1})
        Button:
            text: "Browse"
            on_release: root.webbrowse()
            size_hint: (0.27,1)
            pos_hint: ({'right':1,'top':1})
            font_size: (root.width**2 + root.height**2) / 14**4
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        spacing: 5
        size_hint: (1,0.20)
        Label:
            text: 'Save to:'
            size_hint:(0.32,1)
            pos_hint: ({'x':self.x,'top':1})
            font_size: (root.width**2 + root.height**2) / 14**4
        TextInput:
            id: path
            multiline: False
            font_size: (root.width**2 + root.height**2) / 14**4
            size_hint: (0.72,1)
            pos_hint: ({'x':self.x,'top':1})
        Button:
            text: "Browse"
            on_release: root.filebrowse()
            size_hint: (0.27,1)
            pos_hint: ({'right':1,'top':1})
            font_size: (root.width**2 + root.height**2) / 14**4
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        Label:
            text: ''
        Button:
            text: 'Download'
            on_release: root.downloader()
            size_hint: (0.70,0.20)
            pos_hint: ({'x':self.x,'y':0.6})
            font_size: (root.width**2 + root.height**2) / 14**4
        Label:
            text: ''

<LoginPage>:
    rows: 3
    padding: 8
    get_username: username
    get_password: password
    BoxLayout:
        size_hint: (1,0.30)
        orientation: 'horizontal'
        padding: 5
        Label:
            text: 'Username:'
            size_hint: (0.20,1)
            font_size: (root.width**2 + root.height**2) / 14**4
        TextInput:
            id: username
            multiline: False
            font_size: (root.width**2 + root.height**2) / 14**4
    BoxLayout:
        orientation: 'horizontal'
        size_hint: (1,0.30)
        padding: 5
        Label:
            text: 'Password:'
            size_hint: (0.20,1)
            font_size: (root.width**2 + root.height**2) / 14**4
        TextInput:
            id: password
            multiline: False
            font_size: (root.width**2 + root.height**2) / 14**4
            password: True
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        Label:
            text: ''
        Button:
            text: 'Submit'
            on_release: root.on_submit()
            size_hint: (0.70,0.20)
            pos_hint: ({'x':self.x,'y':0.6})
            font_size: (root.width**2 + root.height**2) / 14**4
        Label:
            text: ''

<Downloading>:
    set_text: newtext
    Label:
        id: newtext
        text: ""
        font_size: 18
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]

<HelpPage>:
    rows: 2
    padding: 8
    set_help: help
    Label:
        id: help
        font_size: 18
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
    BoxLayout:
        orientation: 'horizontal'
        padding: 5
        Label:
            text: ''
        Button:
            text: "Okay"
            on_release: root.close_help()
            size_hint: (0.70,0.20)
            pos_hint: ({'x':self.x,'y':0.6})
            font_size: 20
        Label:
            text: ''
''')


class LoginPage(GridLayout):
    get_password = ObjectProperty()
    get_username = ObjectProperty()

    def on_submit(self):
        print(self.get_username.text, self.get_password.text)
        pass


class HelpPage(GridLayout):
    set_help = ObjectProperty()

    def __init__(self):
        help_texts = ("This App downloads whole directory from Courses and " +
                      "Intranet.\nOfcourse, to download file from courses " +
                      "you have to login once. " +
                      "\nYour username and password will be stored in the "
                      "encrypted form.\nIf you enter wrong password" +
                      " it won't download any file." +
                      "\nYou can reset your password anytime " +
                      "using login button.\n" +
                      "If you find any bug or error in the App " +
                      "you can email me on 201701184@daiict.ac.in")

        super().__init__()

        self.set_help.text = help_texts

    def close_help(self):
        pass


class Downloading(ScrollView):
    set_text = ObjectProperty()

    def __init__(self, select, link, path, username, password):

        self.select = select
        self.link = link
        self.path = path
        self.username = username
        self.password = password
        self.downloading = False

        self.parent_conn, self.child_conn = Pipe()

        p = Process(target=main, args=(self.child_conn, self.select,
                                       self.link, self.path,
                                       self.username, self.password))
        p.start()

        super().__init__()

        self.event = Clock.schedule_interval(self.download_GUI, 0.1)

    def download_GUI(self, a):

        temp = self.parent_conn.recv()

        print(temp)
        if temp == "new":
            self.pretext = self.set_text.text
            self.downloading = True
            return
        if temp == "finish":
            self.downloading = False
            return
        if self.downloading:
            self.set_text.text = self.pretext + temp
            print(self.set_text.text)
            return
        if temp == "end":
            self.event.cancel()
            Clock.schedule_once(exit, 3)
            return
        else:
            self.set_text.text += temp
            return


class Widgets(GridLayout):
    set_path = ObjectProperty()
    set_link = ObjectProperty()
    set_select = ObjectProperty()
    select = 'i'
    try:
        with open("password.json", "r") as f:
            saved_data = json.load(f)
        username = decrypter(saved_data['username'], '836')
        password = decrypter(saved_data['password'], '836')
    except Exception:
        username = None
        password = None

    def intranet(self):
        self.set_select.text = "Intranet"
        self.select = 'i'
        print(self.select)

    def courses(self):
        self.set_select.text = "Courses"
        self.select = 'c'
        print(self.select)

    def filebrowse(self):
        self.show_popup()
        print(self.set_path.text)

    def webbrowse(self):
        if self.select == 'i':
            webbrowser.open("http://intranet.daiict.ac.in")
        else:
            webbrowser.open("http://courses.daiict.ac.in/")

    def downloader(self):

        path = self.set_path.text
        link = self.set_link.text
        d_popup = Downloading(self.select, link, path,
                              self.username, self.password)

        popupWindow = Popup(title="Downloading...",
                            content=d_popup,
                            size_hint=(1, 1))
        popupWindow.open()

    def show_popup(self):

        def _fbrowser_success(instance):
            print(instance.selection)
            self.set_path.text = instance.selection[0]
            # self.path.insert_text(self, substring=instance.selection[0])
            popupWindow.dismiss()

        def _fbrowser_canceled(instance):
            print('cancelled, Close self.')

        def is_dir(directory, filename):
            return isdir(join(directory, filename))

        if platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')],
                              dirselect=BooleanProperty(False),
                              filters=[is_dir]
                              )
        browser.bind(
            on_success=_fbrowser_success,
            on_canceled=_fbrowser_canceled)

        popupWindow = Popup(title="Choose A Directory", content=browser,
                            size_hint=(1, 1))

        popupWindow.open()

    def show_login(self):

        def close():
            self.username = login.get_username.text
            self.password = login.get_password.text
            write_hidden()
            popupWindow.dismiss()

        def write_hidden():

            data = {}
            data['username'] = encrypter(self.username, '836')
            data['password'] = encrypter(self.password, '836')
            HIDDEN = 0x02
            file_name = "password.json"

            prefix = '.' if os.name != 'nt' else ''
            file_name = prefix + file_name

            with open(file_name, 'w') as f:
                json.dump(data, f)

            if os.name == 'nt':
                ret = ctypes.windll.kernel32.SetFileAttributesW(file_name,
                                                                HIDDEN)
                if not ret:
                    raise ctypes.WinError()

        login = LoginPage()

        login.on_submit = close

        popupWindow = Popup(title="Login credential for courses",
                            content=login,
                            size_hint=(0.8, 0.8))
        popupWindow.open()

    def show_help(self):

        def close_popup():

            popupWindow.dismiss()

        help_page = HelpPage()

        help_page.close_help = close_popup

        popupWindow = Popup(title="Login credential for courses",
                            content=help_page,
                            size_hint=(0.8, 0.8))
        popupWindow.open()


class DownloaderApp(App):
    def build(self):
        return Widgets()


if __name__ == "__main__":
    DownloaderApp().run()
