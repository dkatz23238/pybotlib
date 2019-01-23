import os
import glob
import datetime
import time
from shutil import move as moveFile
from pybotlib import VirtualAgent
from pandas import DataFrame, read_excel, read_csv
from pybotlib.utils import check_and_dl_chrome_driver
from os.path import join
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException
import traceback

def getFinancialReports(my_bot, tickers, report):

    """ Downloads an invidiual report from SEC website and saves it to downloads directory """

    for ticker in tickers:
        my_bot.log("searching edgar for %s" % ticker)
        url = "https://www.sec.gov/edgar/searchedgar/companysearch.html"

        my_bot.get(url)
        searchBox = (
            my_bot.find_by_tag_and_attr(
                tag="input",
                attribute="id",
                evaluation_string="cik",
                sleep_secs=3)
            )[0]
        searchBox.clear()
        searchBox.send_keys(ticker, Keys.ENTER)
        typeBox = (
            my_bot.find_by_tag_and_attr(
                tag="input",
                attribute="id",
                evaluation_string="type",
                sleep_secs=3)
            )[0]
        time.sleep(4)
        typeBox.send_keys(report, Keys.ENTER)

        interactiveFields = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="id",
                evaluation_string="interactiveDataBtn",
                sleep_secs=3)
            )
        interactiveFields[0].click()
        exportExcel = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="class",
                evaluation_string="xbrlviewer",
                sleep_secs=3)
            )
        exportExcel = [
            el for el in exportExcel if el.text == "View Excel Document"
            ]

        exportExcel[0].click()

        while not len(glob.glob(os.path.join(my_bot.downloads_dir,  r"*.xlsx"))) > 0:
            time.sleep(1)
            print("waiting for download")

        if os.path.exists(os.path.join(my_bot.downloads_dir,  ticker)):
            pass
        else:
            os.mkdir(os.path.join(my_bot.downloads_dir,  ticker))

        downloadedReport = glob.glob(
            os.path.join(my_bot.downloads_dir,  r"*.xlsx")
            )[0]

        destination = os.path.join(my_bot.downloads_dir,  ticker,"Financial_Report.xlsx")

        moveFile(downloadedReport, destination)
        time.sleep(5)

def getNewsData(my_bot, tickers, names):

    """ Downloads recent news data relating to company name by relevance in the last 24 hours. """

    for index, name in enumerate(names):
        my_bot.log("serching newslookup for %s" % name)
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
            print("Raising Exception")
            raise Exception("Srcap not successful !")

        destination = os.path.join(my_bot.downloads_dir,"%s" %tickers[index] , "NewsData_%s.xlsx" % datetime.datetime.now().strftime("%Y_%m_%d"))
        data = stockData.pop()
        data.to_excel(destination)

def run_robot():

    try:
        # First Stage: Download financial transcripts from EDGAR database
        my_bot = VirtualAgent(
		bot_name="EDGAR_investigator_bot",
		downloads_directory=os.path.join(os.getcwd(), "bot_downloads"),
		firefoxProfile="/home/david/.mozilla/firefox")
        # Creates log file to log an auditable trail and collect errors
        my_bot.create_log_file()
        # Reads tickers from excel into a list
        tickers = read_excel("RPA_input.xlsx")["Company Ticker"].tolist()
        # Initializes the Chrome webdriver
        my_bot.initialize_driver()
        # Collects data from SEC edgar website
        getFinancialReports(my_bot, tickers, report="10-Q")
        # Quits out of driver to finalize stage
        my_bot.quit_driver()
        time.sleep(5)
        # Reads out company names from excel into a list
        names = read_excel("RPA_input.xlsx")["Company Name"].tolist()
        # Second Stage: Extract relevant news article data from newslookup.com
        my_bot.initialize_driver()
        # Gets relevant news articles from past 36 hours
        getNewsData(my_bot, tickers, names)
        # Quit out of driver to finalize second stage
        my_bot.quit_driver()
        my_bot.log_bot_completion()
        print("Robot Complete!")
        print(read_csv(my_bot.logfile_path, encoding="utf-8").set_index("idx"))
    except Exception as e:
        # Logs exceptions
        my_bot.log(message="ERROR: %s" %str(e), tag="execution")
        # One error print out the exception
        print(e)
        # Print out stack trace
        traceback.print_exc()

if __name__ == "__main__":
    # Allows main function only to be executed when explicitly called
    run_robot()
