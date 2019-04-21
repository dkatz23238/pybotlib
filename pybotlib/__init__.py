#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from selenium import webdriver
from pandas import DataFrame
from selenium.webdriver.chrome.options import Options
import os
import glob
import platform
import datetime
import uuid
import csv
from pybotlib.exceptions import NoElementsSatisfyConditions
from time import gmtime, strftime
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as Foptions


DIDNOTINIT = "Use .initialize_driver() to instantiate a webdriver session. "
LOG_FILE_MESSAGE = "Create and initialize logfile using .create_log_file(bot_name) before logging"

def generate_js(tag, atr, evalString):
    """
    Generates js string for web element searching.

    Parameters
    ----------
    tag: str
        HTML tag to search for.

    atr: str
        HTML attribute for which to evaluate when searching the DOM.

    evalString: str
        Used to determine if attribute of HTML is element is equal to this string.


    """
    js = """
    function find_by_tag_and_attr(tag, atr, evalString) {
        const elements = document.getElementsByTagName(tag);
        const arrayLength = elements.length;
        const results = [];
        for (let i = 0; i < arrayLength; i++) {
            if (elements[i].getAttribute(atr) == evalString) {
                results.push(elements[i])
            }
        }
        return results;
    }
    return find_by_tag_and_attr(tag="%s", atr="%s", evalString="%s");
    """ % (tag, atr, evalString)
    return js

class VirtualAgent(object):
    """
    Creates an instance of RPA object:

    RPA objects can be used to create a virtual
    assistant that will cary out a series of event-based
    or stricly scheduled taks.

    Parameters
    ----------
    bot_name: str
        Name of the RPA. Used for logging and identification purposes.

    downloads_directory: str
        Name of the subfolder to which all file downloads from the internet will be downloaded to.

    df: Pandas.DataFrame, optional
        Used to embed a table in the object if needed.

    firefoxProfile: str, optional
        Specific name of the ChromeProfile subfolder to use when using the google chrome driver. Usefull to retain cookies and other web based data.
        Profiles can be found under: "~/.mozilla/firefox/profiles.ini"

    Example:

    human_resources_bot = VirtualAgent(bot_name="HR_bot", downloads_directory="timesheets")
    human_resources_bot.create_log_file()
    human_resources_bot.initialize_driver()
    human_resources_bot.log("WebDriver Initiated")

                    ... ... ...

    Keyword arguments:

    downloads_directory = Directory within downloads
    folder that the RPA's chromedriver will download too.
    Usefull to identify all files downloaded by specific RPA bot.

    """
    def __init__(self,bot_name,downloads_directory,df=None, firefoxProfile=None):

        self.bot_name = bot_name
        self.downloads_dir = downloads_directory
        self.logfile_row_counter = 0


        if df is None:
            pass
        else:
            self.DataFrame = df
            print("DataFrame Provided to RPA")

        if platform.system() == "Linux":
            pass
        else:
            raise Exception("Not Linux System! Please use another branch of pybotlib.")

        opts = Options()

        if firefoxProfile is None:
            # raise Exception("PLEASE PROVIDE Firefox PROFILE")
            pass
        else:
            self.fprefs = webdriver.FirefoxProfile(firefoxProfile)
            self.fprefs.set_preference("browser.download.folderList",2)
            self.fprefs.set_preference("browser.download.dir", self.downloads_dir)
            mime_types = [
                'text/plain',
                'application/pdf',
                'application/vnd.ms-excel',
                'text/csv',
                'application/csv',
                'text/comma-separated-values',
                'application/download',
                'application/octet-stream',
                'binary/octet-stream',
                'application/binary',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ]
            self.fprefs.set_preference("browser.helperApps.neverAsk.saveToDisk", ",".join(mime_types))
            self.fprefs.set_preference("browser.helperApps.alwaysAsk.force", False)
            self.fprefs.set_preference("pdfjs.disabled", True)
            self.fprefs.update_preferences()
            self.fops = Foptions()

        self.firefox_options = opts
        self.driver = None
        self.uid = str(uuid.uuid4().hex)
        self.logfile_path = None

    def create_log_file(self):
        """
        Creates a log csv under "./pybotlib_logs"
        You can log transactional or execution logs once the file has been created.
        """
        bot_name= self.bot_name

        usr = os.environ["USER"]

        if platform.system() == "Linux":

            self.log_path = os.path.join(".", "pybotlib_logs")

        exists = os.path.exists(self.log_path)

        if exists:
            print("log directory already created")
        else:
            glob.os.mkdir(self.log_path)
            print("log directory created: %s" %self.log_path)

        if bot_name is None:
            uid = self.uid
            bot_name = "Unnamed Bot - %s - %s" %(str(uid), str(datetime.datetime.now().strftime("%b %Y")))
            print(bot_name)
        else:
            uid = self.uid
            bot_name = "%s - %s - %s" %(bot_name, str(uid), str(datetime.datetime.now().strftime("%b %Y")))
            print(bot_name)

        logfile = os.path.join(self.log_path, bot_name+".csv")
        self.logfile_path = logfile

        with open(logfile, mode='w') as csv_file:
            fieldnames = [
                "idx",
                "message",
                "tag",
                "timestamp",
                "tz"
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            row = {
                "idx":self.logfile_row_counter,
                "message":"start",
                "tag":"execution",
                "timestamp":str(datetime.datetime.now()),
                "tz":strftime("%z", gmtime()),
            }
            writer.writerow(row)
            self.logfile_row_counter += 1

    def log(self, message, tag="transaction"):
        """
        Logs a message to the currently active log file

        Parameters
        ----------
        message : str
            Message to be logged.
        tag: str
            Tag assoacited to message. Defaults to "transactional"

        """
        if self.logfile_path is None:
            print(LOG_FILE_MESSAGE)
        else:

           with open(self.logfile_path, mode='a') as csv_file:
            fieldnames = [
                "idx",
                "message",
                "tag",
                "timestamp",
                "tz"
            ]

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            row = {
                "idx":self.logfile_row_counter,
                "message":message,
                "tag":tag,
                "timestamp":str(datetime.datetime.now()),
                "tz":strftime("%z", gmtime()),
            }
            writer.writerow(row)
            self.logfile_row_counter += 1

    def log_bot_completion(self):
        """ Logs that the RPA has sucesfully completed. To be used at the very end of the RPA"""
        if self.logfile_path is None:
            print(LOG_FILE_MESSAGE)
        else:

           with open(self.logfile_path, mode='a') as csv_file:
            fieldnames = [
                "idx",
                "message",
                "tag",
                "timestamp",
                "tz"
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            row = {
                "idx":self.logfile_row_counter,
                "message":"end",
                "tag":"execution",
                "timestamp":str(datetime.datetime.now()),
                "tz":strftime("%z", gmtime()),
            }
            writer.writerow(row)
            self.logfile_row_counter += 1

    def set_DataFrame(self, df):
        """ Setter for a pandas DataFrame """
        self.DataFrame = df

    def initialize_driver(self):
        """ Inits a new Chrome driver session to interact with applications through the web. """
        self.driver = webdriver.Firefox(
            executable_path="./geckodriver",
            firefox_profile=self.fprefs,
            firefox_options=self.fops)

    def get(self, url):
        """ Directs the Chrome driver to a URL"""
        if self.driver is None:
            print(DIDNOTINIT)
        else:
            self.driver.get(url)

    def use_javascript(self, script):
        """ Executes javascript code into the current running webpage. """
        if self.driver is None:
            print(DIDNOTINIT)
        else:
            return self.driver.execute_script(script)

    def find_by_tag_and_attr(self, tag, attribute, evaluation_string, sleep_secs, return_many=True):
        """
        Usefull function to scan a web site for elements that satisfy specific conditions.
        This function is accelerated with javascript.

        Parameters
        ----------
        tag : str
            HTML tag to begin search for. If the element we seek is an <input> we would pass the argument "input".

        attribute: str
            Which attribute of the HTML element do we evaluate in order to interact with a webpage.
            To name a few: "class", "id", or "placeholder", are all possible examples.

        evaluation_string: str
            What text should we evaluate when searching the elements on the page. If our attribute is "id" and
            evaluation string is "001" we will reduce our search the the elements that id == "001".

        sleep_secs: float
            How many seconds to sleep before executing search

        return_many: bool, optional
            Should the method return a list or an invidiual element

        Returns
        ----------
        list or selenium.webdriver.remote.webelement
            Either returns a list of webelement objects or an individual webelement object depending on the return_many argument.

        Example:
        my_bot.find_by_tag_and_attr(
            tag="a",
            attribute="class",
            evalutaion_string="special_class",
            sleep_secs=0.2)

        """
        if self.driver is None:
            print(DIDNOTINIT)
        else:
            sleep(sleep_secs)
            js = generate_js(tag=tag, atr=attribute, evalString=evaluation_string)
            elements = self.driver.execute_script(js)
            if len(elements) > 0:
                if return_many:
                    return elements
                else:
                    return elements[0]
            else:
                raise NoElementsSatisfyConditions("No elements found satisfying conditions!")
    def quit_driver(self):
        """ Quits out of the web driver."""
        #self.driver.close()
        self.driver.close()
