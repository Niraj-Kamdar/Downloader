import mechanize
import subprocess
import time


filetypes = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png",
             ".ppt", ".pptx", ".zip", ".rar", ".txt", ".rtf", ".mp3", ".mkv",
             ".mp4", ".webm", ".ogg", ".3gp", ".avi", ".mov", ".gif",
             ".7z", ".c", ".cpp", ".py", ".java", ".epub", ".sh"]


def downloader(download, p):
    global filetypes
    try:
        br.open(download)
    except:
        pass
    myfiles = []
    mydir = []
    for link in br.links():
        for type in filetypes:
            if type in str(link):
                myfiles.append(link)
        if link.text[-1] == "/":
            mydir.append(link)
    for link in myfiles:
        downloadlink(download, link, p)
    for link in mydir:
        n = len(link.text)
        try:
            subprocess.check_output(
                "mkdir " + '''\"{}'''.format(p) + '\\' + '''{}\"'''.format(link.text[:n-1]), shell=True)
        except:
            pass
        downloader(download + link.text.replace(" ", "%20"),
                   p + '\\' + link.text[:n-1])


def downloadlink(d, l, po):
    global error
    global c
    if po[-1] == '\\':
        f = open(po + l.text, "wb")
    else:
        f = open(po + '\\' + l.text, "wb")
    try:
        br.open(d + l.text.replace(" ", "%20"))
        f.write(br.response().read())
        print(l.text + " downloaded")
        c = c + 1
    except:
        error.append(l.text)


if __name__ == '__main__':
    error = []
    c = 0
    print("Mass download files and folders from Intranet")
    download = input(
        "please input URL from where you want to download: ")
    path = input(
        "enter download path: ")
    br = mechanize.Browser()
    t1 = time.perf_counter()
    downloader(download, path)
    t2 = time.perf_counter()
    for i in error:
        print("download failed : link generation error : {}".format(i))
    print("\n\n")
    print("{} files downloaded in {} seconds!".format(c, round(t2 - t1, 2)))
    print("Created by ALPHA")
    input()
