import os
import glob
import datetime
import time
from shutil import move as moveFile
from pybotlib import my_RPA
from pandas import DataFrame, read_excel
from pybotlib.utils import CheckCDriver
from os.path import join 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException

def getFinancialReports(my_bot, tickers, report):

    """ Downloads an invidiual report from SEC website and saves it to downloads directory """

    for ticker in tickers:
        url = "https://www.sec.gov/edgar/searchedgar/companysearch.html"
       
        my_bot.get(url)
        searchBox = (
            my_bot.find_by_tag_and_attr(
                tag="input",
                attribute="id",
                evaluation_string="cik",
                sleep_secs=0.5)
            )[0]
        searchBox.clear()
        searchBox.send_keys(ticker, Keys.ENTER)
        typeBox = (
            my_bot.find_by_tag_and_attr(
                tag="input",
                attribute="id",
                evaluation_string="type",
                sleep_secs=0.5)
            )[0]
        typeBox.send_keys(report, Keys.ENTER)

        interactiveFields = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="id",
                evaluation_string="interactiveDataBtn",
                sleep_secs=0.5)
            )
        interactiveFields[0].click()
        exportExcel = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="class",
                evaluation_string="xbrlviewer",
                sleep_secs=0.5)
            )
        exportExcel = [
            el for el in exportExcel if el.text == "View Excel Document"
            ]
        
        exportExcel[0].click()

        while not len(glob.glob(my_bot.downloads_dir + r"\\*.xlsx")) > 0:
            time.sleep(1)

        if os.path.exists(my_bot.downloads_dir + r"\\%s" % ticker):
            pass
        else:
            os.mkdir(my_bot.downloads_dir + r"\\%s" % ticker)
        
        downloadedReport = glob.glob(
            my_bot.downloads_dir +  r"\\*.xlsx"
            )[0]
        
        destination = my_bot.downloads_dir + r"\\%s" % ticker + r"\\Financial_Report.xlsx"
        moveFile(downloadedReport, destination)
        time.sleep(5)
    
def getNewsData(my_bot, names):

    """ Downloads recent news data relating to company name by relevance in the last 24 hours. """

    for index, name in enumerate(names):
        url = "http://newslookup.com/"
        stockData = []
        my_bot.get(url)
        searchBox = my_bot.find_by_tag_and_attr(
            tag="input",
            attribute="class",
            evaluation_string="form-control",
            sleep_secs=0.1,
        )
        searchBox[0].clear()
        searchBox[0].send_keys(name, Keys.ENTER)
        # expands for more results
        for i in range(3):
            try:
                my_bot.find_by_tag_and_attr(
                    tag="button",
                    attribute="id",
                    evaluation_string="more-btn",
                    sleep_secs=3
                    )[0].click()
            except:
                break
        
        titles = my_bot.find_by_tag_and_attr(tag="a", attribute="class", evaluation_string="title", sleep_secs=2)
        title_texts = [i.text for i in titles]
        title_links = [i.get_attribute("href") for i in titles]

        times = [  i.text for i in 
            my_bot.find_by_tag_and_attr(tag="span", attribute="class", evaluation_string="stime", sleep_secs=0.1)
            ]


        scraped_success = (len(titles) == len(title_links) == len(title_texts) == len(times))

        if scraped_success:

            current_page = {}
            current_page["article_title"] = title_texts
            current_page["article_link"] = title_links
            current_page["article_publish"] = times
            stockData.append(DataFrame(current_page).drop_duplicates("article_title"))

        else:

            raise Exception("error please check code")

        destination = my_bot.downloads_dir + "\\%s"%tickers[index] + "\\NewsData_%s.xlsx" % datetime.datetime.now().strftime("%Y_%m_%d")
        data = stockData.pop()
        data.to_excel(destination)

# First Stage: Download financial transcripts from EDGAR database
my_bot = my_RPA(bot_name="EDGAR_investigator_bot", downloads_directory = "EDGAR_bot" )
# Creates log file to log an auditable trail and collect errors
my_bot.create_log_file()
# Reads tickers from excel into a list
tickers = read_excel("RPA_input.xlsx")["Company Ticker"].tolist()
# Initializes the Chrome webdriver
my_bot.initialize_driver()
# Collects data from SEC edgar website
getFinancialReports(my_bot, tickers, report="10-Q")
# Quits out of driver to finalize stage
my_bot.driver.quit()
time.sleep(5)

# Reads out company names from excel into a list
names = read_excel("RPA_input.xlsx")["Company Name"].tolist()
# Second Stage: Extract relevant news article data from newslookup.com
my_bot.initialize_driver()
# Gets relevant news articles from past 36 hours
getNewsData(my_bot, names)
# Quit out of driver to finalize second stage
my_bot.driver.quit()
print("Robot Complete!")
