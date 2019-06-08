from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from multiprocessing import Pipe, Process, freeze_support
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from pySmartDL import SmartDL
import webbrowser
import mechanize
import subprocess
import time
import json
import ctypes
import os
import kivy
import sys


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
            conn.send("new")
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
                conn.send("new")
                conn.send(l.text + " downloaded\n")
            else:
                conn.send("new")
                print(l.text)
                conn.send(l.text)
                obj = SmartDL(l.absolute_url, po, progress_bar=False)
                obj.start(blocking=False)
                while not obj.isFinished():
                    d_state = {}
                    d_state['complete'] = False
                    d_state['speed'] = obj.get_speed(human=True)
                    d_state['dl_size'] = obj.get_dl_size(human=True)
                    d_state['total_size'] = obj.get_final_filesize(human=True)
                    d_state['eta'] = obj.get_eta(human=True)
                    d_state['progress'] = obj.get_progress()*100
                    conn.send(d_state)
                    time.sleep(0.2)

                if obj.isSuccessful():
                    d_state = {}
                    d_state['complete'] = True
                    d_state['total_size'] = obj.get_final_filesize(human=True)
                    conn.send(d_state)
                else:
                    print("There were some errors:")
                    for e in obj.get_errors():
                        print(str(e))
                return
        except Exception as e:
            print(e)
            # conn.send("error"+str(e))
            return

    if select == 'c':
        br.open("https://courses.daiict.ac.in/login/index.php")
        br.select_form(nr=0)
        br.form['username'] = username
        br.form['password'] = password
        br.submit()
        print("you have succesfully login into your account.")
        conn.send("new")
        conn.send("you have succesfully login into your account.")
        conn.send("new")
        conn.send("Sometimes downloading from courses takes too much time.")
        conn.send("new")
        conn.send("So,please wait even if it says Not responding")

    print("please wait if you don't see any error it's downloading.")
    # conn.send("please wait if you don't see any error it's downloading.")

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
    my_grid: mygrid
    GridLayout:
        cols: 1
        size_hint_y : None
        height: self.minimum_height
        id: mygrid

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
                      "you can email me on 201701184@daiict.ac.in\n\n"
                      "Note: support for courses is in Beta stage")

        super().__init__()

        self.set_help.text = help_texts

    def close_help(self):
        pass


class Downloading(ScrollView):

    my_grid = ObjectProperty()

    def __init__(self, select, link, path, username, password):

        self.select = select
        self.link = link
        self.path = path
        self.username = username
        self.password = password
        self.p_bar = []
        self.stat = []
        self.downloading = False
        self.parent_conn, self.child_conn = Pipe()

        p = Process(target=main, args=(self.child_conn, self.select,
                                       self.link, self.path,
                                       self.username, self.password))
        p.start()

        super().__init__()

        self.event = Clock.schedule_interval(self.download_GUI, 0.1)
        self.my_grid.bind(minimum_height=self.my_grid.setter('height'))

    def newFile(self, title):
        self.stat.append(Label(text='', size_hint=(1, None), height=30))
        self.p_bar.append(ProgressBar())
        self.my_grid.add_widget(
            Label(text=title, size_hint=(1, None), height=30))
        self.my_grid.add_widget(self.stat[-1])
        self.my_grid.add_widget(self.p_bar[-1])

    def download_GUI(self, a):

        if self.select != 'c':

            temp = self.parent_conn.recv()

            print(temp)

            if temp == "new":
                self.downloading = True
                return
            if self.downloading:
                self.newFile(temp)
                self.downloading = False
                return
            if isinstance(temp, dict):
                self.complete = temp['complete']
                if not self.complete:
                    status = "{0}/{1} @ {2}  ETA: {3}".format(temp['dl_size'],
                                                              temp['total_size'],
                                                              temp['speed'],
                                                              temp['eta'])
                    self.stat[-1].text = status
                    self.p_bar[-1].value = temp['progress']
                    return
                final = temp['total_size']
                status = "{0}/{1}   {2}  ETA: {3}".format(
                    final, final, '', '0s')
                self.stat[-1].text = status
                self.p_bar[-1].value = 100
                return
            if temp == "end":
                self.event.cancel()
                # Clock.schedule_once(exit, 5)
                self.close()
        else:

            temp = self.parent_conn.recv()
            print(temp)
            if temp == "end":
                self.event.cancel()
                # Clock.schedule_once(exit, 5)
                self.close()
            if temp == 'new':
                self.downloading = True
                self.set_text = Label(text="",
                                      font_size=18,
                                      size_hint=(1, None),
                                      height=30)
                self.my_grid.add_widget(self.set_text)
                return
            if self.downloading:
                self.set_text.text = temp
                self.downloading = False
                return

    def close(self):
        print("closing self")


class Widgets(GridLayout):
    set_path = ObjectProperty()
    set_link = ObjectProperty()
    set_select = ObjectProperty()
    select = 'i'
    # you have to set this key first in your environment variable
    key = os.environ.get('DECRYPT_KEY')
    try:
        with open("password.json", "r") as f:
            saved_data = json.load(f)
        username = decrypter(saved_data['username'], key)
        password = decrypter(saved_data['password'], key)
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

        def close_popup():

            popupWindow.dismiss()

        path = self.set_path.text
        link = self.set_link.text
        d_popup = Downloading(self.select, link, path,
                              self.username, self.password)
        d_popup.close = close_popup

        popupWindow = Popup(title="Downloading...",
                            content=d_popup,
                            size_hint=(1, 1))
        popupWindow.open()

    def show_popup(self):
        if os.name == 'nt':
            subprocess.Popen(r'explorer /select,"C:\"')
        else:
            pass

    def show_login(self):

        def close():
            self.username = login.get_username.text
            self.password = login.get_password.text
            write_hidden()
            popupWindow.dismiss()

        def write_hidden():

            data = {}

            data['username'] = encrypter(self.username, self.key)
            data['password'] = encrypter(self.password, self.key)
            HIDDEN = 0x02
            file_name = "password.json"

            prefix = '.' if os.name != 'nt' else ''
            file_name = prefix + file_name
            try:
                with open(file_name, 'w') as f:
                    json.dump(data, f)
            except Exception:
                os.remove(file_name)
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

        popupWindow = Popup(title="Help",
                            content=help_page,
                            size_hint=(0.8, 0.8))
        popupWindow.open()


def resourcePath():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)

    return os.path.join(os.path.abspath("."))


class DownloaderApp(App):
    def build(self):
        return Widgets()


if __name__ == "__main__":
    freeze_support()
    kivy.resources.resource_add_path(resourcePath())  # add this line
    DownloaderApp().run()
