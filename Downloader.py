import mechanize
import subprocess
import time
import json
from getpass import getpass
from pySmartDL import SmartDL as sdl


filetypes = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png",
             ".ppt", ".pptx", ".zip", ".rar", ".txt", ".rtf", ".mp3", ".mkv",
             ".mp4", ".webm", ".ogg", ".3gp", ".avi", ".mov", ".gif", ".psd",
             ".7z", ".c", ".cpp", ".py", ".java", ".epub", ".sh", ".bmp",
             ".exe", ".tar"]


def downloader(download, p):
    global filetypes
    try:
        br.open(download)
    except Exception as e:
        if "b'" in e:
            s = str(e).split("'")
            lenth = len(s[0])
            s[0] = s[0][:lenth-1]
            for i in s:
                print(i, end="")
            print()
        else:
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
                                    '\\' + '''{}\"'''.format(link.text[:n-1]),
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
        if "b'" in e:
            s = str(e).split("'")
            lenth = len(s[0])
            s[0] = s[0][:lenth-1]
            for i in s:
                print(i, end="")
            print()
        else:
            print(e)
        return
    for link in br.links():
        if ".pdf" in link.text.lower():
            downloadlink(link, p, False, True)
        elif " File" in link.text:
            downloadlink(link, p, False, False)


def downloadlink(l, po, select=True, file=None):
    global c
    if not l.text:
        return
    if not select:
        if file:
            if po[-1] == '\\':
                f = open(po + l.text, "wb")
            else:
                f = open(po + '\\' + l.text, "wb")
        else:
            br.open(l.absolute_url)
            for i in br.links():
                if ".pdf" in i.text:
                    l = i
                    break
            f = open(po + '\\' + l.text, "wb")
    try:
        if not select:
            br.open(l.absolute_url)
            f.write(br.response().read())
            print(l.text + " downloaded")
        else:
            print()
            url = l.absolute_url
            print(l.text)
            obj = sdl(url, po)
            obj.start()
            print()
            print('='*100)
            print()

        c = c + 1
    except Exception as e:
        if "b'" in e:
            s = str(e).split("'")
            lenth = len(s[0])
            s[0] = s[0][:lenth-1]
            for i in s:
                print(i, end="")
            print()
        else:
            print(e)
        return


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


if __name__ == '__main__':
    c = 0
    skey = "836"
    br = mechanize.Browser()
    # br.set_handle_equiv(False)
    # br.set_handle_robots(False)
    # br.set_handle_referer(False)
    # br.set_handle_refresh(False)
    print("Mass download files and folders from Intranet and Courses")
    print("Note: if you enter wrong password for courses it won't download.")
    print("Note: To reset password delete 'pass.json' file.")
    print("Note: it won't download embedded PDF file of courses.")
    print("\n\n")
    select = input(
        "Intranet or Courses (i) for intranet and (c) for courses ") or 'i'
    if select.lower() == 'c':
        try:
            with open("pass.json", "r") as f:
                a = json.load(f)
                a['username'] = decrypter(a['username'], skey)
                a['password'] = decrypter(a['password'], skey)
        except Exception:
            a = {}
            b = {}
            print("You just has to enter username and password for once!")
            print("Your password will be stored in 'pass.json' \
                   in encrypted format.")
            a["username"] = input("enter your student id: ")
            a["password"] = getpass()
            with open("pass.json", "w") as f:
                b['username'] = encrypter(a['username'], skey)
                b['password'] = encrypter(a['password'], skey)
                json.dump(b, f)
        br.open("https://courses.daiict.ac.in/login/index.php")
        br.select_form(nr=0)
        br.form['username'] = a['username']
        br.form['password'] = a['password']
        br.submit()
        print("you have succesfully login into your account.")
    download = input(
        "please input URL from where you want to download: \n")
    path = input(
        "please input folder path location where you want to store data: \n")
    print("please wait if you don't see any error it's downloading.")
    t1 = time.perf_counter()
    if select.lower() != 'c':
        downloader(download, path)
    else:
        c_downloader(download, path)
    t2 = time.perf_counter()
    print("\n\n")
    print("{} files downloaded in {} seconds!".format(c, round(t2 - t1, 2)))
    print("Created by ALPHA")
    input()
