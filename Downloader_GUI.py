from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
import webbrowser
import mechanize
import subprocess
import time
c = 0
filetypes = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png",
             ".ppt", ".pptx", ".zip", ".rar", ".txt", ".rtf", ".mp3", ".mkv",
             ".mp4", ".webm", ".ogg", ".3gp", ".avi", ".mov", ".gif", ".psd",
             ".7z", ".c", ".cpp", ".py", ".java", ".epub", ".sh", ".bmp",
             ".exe", ".tar"]


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


def main(select, download, path, username=None, password=None):
    br = mechanize.Browser()
    # br.set_handle_equiv(False)
    # br.set_handle_robots(False)
    # br.set_handle_referer(False)
    # br.set_handle_refresh(False)

    def downloader(download, p):
        global filetypes
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

    def c_downloader(download, p):
        global filetypes
        try:
            br.open(download)
        except Exception as e:
            print(e)
            return
        for link in br.links():
            if ".pdf" in link.text.lower():
                downloadlink(link, p)
            elif " File" in link.text:
                downloadlink(link, p, False)

    def downloadlink(l, po, select=True):
        global c
        if not l.text:
            return
        if select:
            if po[-1] == '\\':
                f = open(po + l.text, "wb")
            else:
                f = open(po + '\\' + l.text, "wb")
        else:
            n = len(l.text)
            f = open(po + '\\' + l.text[:n-5] + ".pdf", "wb")
        try:
            br.open(l.absolute_url)
            f.write(br.response().read())
            print(l.text + " downloaded")
            c = c + 1
        except Exception as e:
            print(e)
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
    print("please wait if you don't see any error it's downloading.")
    t1 = time.perf_counter()
    if select != 'c':
        downloader(download, path)
    else:
        c_downloader(download, path)
    t2 = time.perf_counter()
    print("{} files downloaded in {} seconds!".format(c, round(t2 - t1, 2)))
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
            font_size: 18
        TextInput:
            id: username
            multiline: False
            font_size: 18
    BoxLayout:
        orientation: 'horizontal'
        size_hint: (1,0.30)
        padding: 5
        Label:
            text: 'Password:'
            size_hint: (0.20,1)
            font_size: 18
        TextInput:
            id: password
            multiline: False
            font_size: 18
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

<P>:
    Label:
        text: "You pressed the button"
        size_hint: 0.6, 0.2
        pos_hint: {"x":0.2, "top":1}

    Button:
        text: "You pressed the button"
        size_hint: 0.8, 0.2
        pos_hint: {"x":0.1, "y":0.1}
''')


class LoginPage(GridLayout):
    get_password = ObjectProperty()
    get_username = ObjectProperty()

    def on_submit(self):
        pass


class Widgets(GridLayout):
    set_path = ObjectProperty()
    set_link = ObjectProperty()
    set_select = ObjectProperty()
    username = None
    password = None
    select = 'i'

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
        webbrowser.open("http://intranet.daiict.ac.in")

    def downloader(self):
        path = self.set_path.text
        link = self.set_link.text
        main(self.select, link, path, self.username, self.password)

    def show_popup(self):
        subprocess.Popen(r'explorer /select,"C:\"')

    def show_login(self):

        def close():
            self.username = login.get_username.text
            self.password = login.get_password.text
            popupWindow.dismiss()

        login = LoginPage()

        login.on_submit = close

        popupWindow = Popup(title="Login credential for courses", content=login,
                            size_hint=(None, None), size=(700, 500))
        popupWindow.open()


class login(GridLayout):
    pass


class Intranet_DownloaderApp(App):
    def build(self):
        return Widgets()


if __name__ == "__main__":
    Intranet_DownloaderApp().run()
