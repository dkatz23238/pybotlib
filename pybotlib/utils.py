from os import mkdir
from requests import get
from shutil import copy
import StringIO
from zipfile import ZipFile
from os.path import exists
import platform

def CheckCDriver():
    if platform.system() == "Windows":

        try:
            mkdir(r"C:\chromedriver_win32")
        except:
            pass
        if exists(r"C:\chromedriver_win32\chromedriver.exe"):
            print("CDrive Check Complete!")
        else:
            r = get('https://chromedriver.storage.googleapis.com/2.38/chromedriver_win32.zip' , stream=True)
            z = ZipFile(StringIO.StringIO(r.content))
            z.extractall(r"c:\chromedriver_win32")
            print("")
            print("CDrive Check Complete!")
        if exists(r"C:\chromedriver_win32\Disable-Download-Bar_v1.5.crx"):
            print("Disable Bar Already In Folder")
        else:
            copy("Disable-Download-Bar_v1.5.crx", r"C:\chromedriver_win32\Disable-Download-Bar_v1.5.crx")
    else:
        return Exception("Only Supported For Windows")
