# Downloader
This is a windows application(written in python) which can mass download files or directories from internet. Download compiled binary file from [here](https://github.com/Niraj-Kamdar/Downloader/releases/download/v0.1/Downloader_0.1.exe)

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a Windows system.


### Prerequisites

You will need `python 3.x` installed

### Installing

After cloning/downloading this repository you have to install necessary packages from requirements.txt with following command

```
pip install -r requirements.txt
```
Now set up Windows Environment Variable with following instructions:
* Goto `Control Panel\System and Security\System`
* Select `Environment Variables...` from `Advanced system settings` menu
* Now add new user variable with name `DECRYPT_KEY` and set any 3-digit integer as value.

## Deployment

If you want to create portable executable file than run following command
```
pyinstaller --onefile -y --clean --windowed --name Downloader_0.1 --icon dwnd.ico --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant-moduletwisted Downloader_GUI.py
```
You can change name and icon of exe file with `--name` and `--icon` options</br>
This will create spec file of your given name. In our case it's `Downloader_0.1.spec`</br>
Make following changes to spec file:</br>
* Add `from kivy.deps import sdl2, glew` below `# -*- mode: python -*-`
* Remove `[],` from `exe` block and Add `*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],`

Now recompile your code with following command:
```pyinstaller Downloader_0.1.spec```</br>
It will create portable executable named `Downloader_0.1.exe` inside dist directory.</br>
You can run it on any Windows machine.

## Built With

* [PyInstalller](https://www.pyinstaller.org/) -  freezes (packages) Python applications into stand-alone executables
* [kivy](https://kivy.org/#home) - Cross-platform GUI framework
* [Mechanise](https://mechanize.readthedocs.io/en/latest/) - Stateful programmatic web browsing in Python.
* [pySmartDL](https://itaybb.github.io/pySmartDL/) -  A full-pledged smart download manager for Python 



