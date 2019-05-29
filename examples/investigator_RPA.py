import os
import glob
import datetime
import time


from shutil import move as moveFile
from shutil import rmtree as removeDirectoryAndContents
from shutil import make_archive
from pybotlib import VirtualAgent
from pandas import DataFrame, read_excel, read_csv
from pybotlib.utils import  pandas_read_google_sheets
from os.path import join
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException
import traceback

from pybotlib.utils import create_minio_bucket, write_file_to_minio_bucket

SLEEPSECONDS = 5
# First let's get the enviornment variables
try:
# Minio File store URI for uploading the output files
    MINIO_URI = os.environ["MINIO_URL"]
    MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
    MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]
    MINIO_OUTPUT_BUCKET_NAME = os.environ["MINIO_OUTPUT_BUCKET_NAME"]
    # Business logic input file decoupled using Google Drive Sheets
    GSHEET_ID = os.environ["GSHEET_ID"]
except KeyError as e:
    print("You must instansiate enviornment variables in env-vars.sh")
    raise e

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
                sleep_secs=SLEEPSECONDS)
            )[0]
        searchBox.clear()
        searchBox.send_keys(ticker, Keys.ENTER)
        typeBox = (
            my_bot.find_by_tag_and_attr(
                tag="input",
                attribute="id",
                evaluation_string="type",
                sleep_secs=SLEEPSECONDS)
            )[0]
        time.sleep(4)
        typeBox.send_keys(report, Keys.ENTER)

        interactiveFields = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="id",
                evaluation_string="interactiveDataBtn",
                sleep_secs=SLEEPSECONDS)
            )
        interactiveFields[0].click()
        exportExcel = (
            my_bot.find_by_tag_and_attr(
                tag="a",
                attribute="class",
                evaluation_string="xbrlviewer",
                sleep_secs=SLEEPSECONDS)
            )
        exportExcel = [
            el for el in exportExcel if el.text == "View Excel Document"
            ]

        exportExcel[0].click()

        while not len(glob.glob(os.path.join(my_bot.downloads_dir,  r"*.xlsx"))) > 0:
            time.sleep(3)
            print("waiting for download")
            exportExcel[0].click()

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

def run_robot():

    input_dataframe = pandas_read_google_sheets(GSHEET_ID)

    try:
        # First Stage: Download financial transcripts from EDGAR database
        my_bot = VirtualAgent(
		bot_name="EDGAR_investigator_bot",
		downloads_directory=os.path.join(os.getcwd(), "bot_downloads"),
		firefoxProfile=os.path.join("/","home",os.environ["USER"], ".mozilla", "firefox"))
        # Creates log file to log an auditable trail and collect errors
        my_bot.create_log_file()
        # Reads tickers from excel into a list
        tickers = input_dataframe["Company Ticker"].tolist()
        # Initializes the Chrome webdriver
        my_bot.initialize_driver()
        # Collects data from SEC edgar website
        getFinancialReports(my_bot, tickers, report="10-Q")
        # Quits out of driver to finalize stage
        my_bot.quit_driver()
        time.sleep(5)
        # Reads out company names from excel into a list
        my_bot.log_bot_completion()
        # print("Robot Complete!")
        # print(read_csv(my_bot.logfile_path, encoding="utf-8").set_index("idx"))

        ########## CLEAN UP AND OUTPUT DATA PERSISTANCE ##########
        create_minio_bucket(MINIO_URI, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_OUTPUT_BUCKET_NAME )

        # Write geckodriver logs to minio
        if os.path.exists("./geckodriver.log"):
            write_file_to_minio_bucket(
                MINIO_URI,
                MINIO_ACCESS_KEY,
                MINIO_SECRET_KEY,
                MINIO_OUTPUT_BUCKET_NAME,
                "geckodriver.log")
                # Write pybotlib logs to minio

        output_data_filename = "pybotlib-logs"
        compression_method = "zip"
        archived_file = make_archive(output_data_filename, compression_method, "./pybotlib_logs/")
        write_file_to_minio_bucket(
            MINIO_URI,
            MINIO_ACCESS_KEY,
            MINIO_SECRET_KEY,
            MINIO_OUTPUT_BUCKET_NAME,
            "%s.%s" % (output_data_filename, compression_method)
            )


        for f in glob.glob("./pybotlib_logs/.*csv"):
            write_file_to_minio_bucket(
                MINIO_URI,
                MINIO_ACCESS_KEY,
                MINIO_SECRET_KEY,
                MINIO_OUTPUT_BUCKET_NAME,
                f)
        # Business data output is stored in bot_downloads.
        # We will zip this folder as stock-data.zip and upload it as a single file.
        output_data_filename = "financial-data"
        compression_method = "zip"
        archived_file = make_archive(output_data_filename, "zip", "./bot_downloads/")
        write_file_to_minio_bucket(
            MINIO_URI,
            MINIO_ACCESS_KEY,
            MINIO_SECRET_KEY,
            MINIO_OUTPUT_BUCKET_NAME,
            "%s.%s" % (output_data_filename, compression_method)
            )
        # Clean up and delete all the files we need
        removeDirectoryAndContents("./pybotlib_logs", ignore_errors=True)
        removeDirectoryAndContents("./bot_downloads", ignore_errors=True)
        # Remove the zip file we uploaded to minio
        for f in glob.glob("./*.log"):
            os.remove(f)
        for f in glob.glob("./*.zip"):
            os.remove(f)

    except Exception as e:
        # Logs exceptions
        my_bot.log(message="ERROR: %s" %str(e), tag="execution")

        try:
            my_bot.driver.quit()
        except:
            pass
        # Print out stack trace
        traceback.print_exc()
        # raise error if fails
        raise e

if __name__ == "__main__":
    # Allows main function only to be executed when explicitly called

    env_vars = (
        MINIO_URI,
        MINIO_ACCESS_KEY,
        MINIO_SECRET_KEY,
        MINIO_OUTPUT_BUCKET_NAME

    )

    print("ACCESSED ENVIORNMENT VARIABLES")
    for var in env_vars:
        print(var)

    run_robot()
