import datetime
import email
import email.header
import getpass
import imaplib
import os
import platform
import smtplib
import ssl
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import time
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from os import mkdir
from os.path import exists
from shutil import copy
from zipfile import ZipFile
import subprocess
from subprocess import PIPE

import mailparser as mailparser
import requests
from pandas import read_csv
from requests import get
import pygsheets


import subprocess
from subprocess import PIPE

from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
import os

def get_geckodriver():
    """Fetches latest version of geckodriver to automate firefox via the Selenium webdriver.

    This function uses GNU wget. Make sure it is installed on the system before calling get_geckodriver()
    
    """

    commands_1 = ["wget", "-nv", "https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz",]
    commands_2 = ["tar", "xvfz", "geckodriver-v0.23.0-linux64.tar.gz"]
    commands_3 = ["rm","geckodriver-v0.23.0-linux64.tar.gz"]

    process = subprocess.Popen(commands_1)
    sc1 = process.wait()
    process = subprocess.Popen(commands_2)
    sc2 = process.wait()
    process = subprocess.Popen(commands_3)
    sc3 = process.wait()

    if not sc1 == sc2 == sc3 == 0:
        raise Exception("Status Code not 0 for geckodriver install!!!")
    else:
        print("Geckodriver Install Success")


def dt_parse(t):
    """Parses out datetime from email msg format.

    Args:
      t(str): t is a string containing an RFC 2822 date, such as "Mon, 20 Nov 1995 19:12:08 -0500".

    Returns:
      datetime.datetime: A datetime.datetime object.
    """
    return (
       datetime.fromtimestamp(
           time.mktime(
               email.utils.parsedate(t)
           )
       )
   )

def return_emails_from_IMAP(email_account, password, email_folder, search_term="ALL", url='imap.gmail.com'):

    """Returns a list of mailparser.MailParser objects from an email address using IMAP.
    
    Used to search a specific IMAP email folder and return a list of individual mailparser.MailParser objects.
    Will return no values if the login, folder, or search fails. You can replace search_term with other fields such as "UnSeen" or "Seen".

    Args:
      email_account(str): Email address to read inbox from in string format.
      password(str): Password for associated email_account.
      email_folder(str): Which IMAP folder to return emails from.
      search_term(str): Term that is used to search in email folder. Defaults to all.
      url(str): IMAP server url. Defaults to imap.gmail.com for use with google gmail accounts.

    Returns:
      list: A list of mailparser.MailParser objects retrieved from the email server.
    """

    M = imaplib.IMAP4_SSL(url)

    try:
        rv, data = M.login(email_account, password)
    except imaplib.IMAP4.error:
        print("Login Failed. Check Credentials and imap url.")
        return

    rv, data = M.select(email_folder)

    if rv != 'OK':
        print("Email folder not found.")
        return

    response = []
    rv, data = M.search(None, search_term)

    if rv != 'OK':
        print("No unSeen Messages")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            #return

        msg = email.message_from_string(data[0][1])
        parsed_msg = mailparser.parse_from_string(msg.as_string())
        response.append(parsed_msg)
    M.logout()
    return response

def save_emails_to_CWD(list_of_mails):
    """ Saves a list of mailparser.MailParser objects to CWD.

    Takes as input a list of mailparser.MailParser objects and saves the emails to current working directory under a folder called pybotlib_emails.
    Headers and body are saved as individual txt files inside a folder named after the subject and date recieved.
    Attachments are also saved into said folder.

    Args:
      list_of_mails(list): A list of mailparser.MailParser objects.

    Returns:
      None.

    """


    if not os.path.exists("pybotlib_emails"):
        os.mkdir("pybotlib_emails")
    for mail in list_of_mails:

        if type(mail) != mailparser.mailparser.MailParser:
            raise Exception("save_emails_to_cwd ony takes in a list of mailparser.MailParser objects")

        header = mail.headers_json
        body = mail.body
        mail_date = dt_parse(mail.Date).strftime("%m-%d-%Y %H.%M.%S")

        folder_name = os.path.join("pybotlib_emails", mail.headers["Message-ID"].split("-")[1] +" " + mail_date)

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        f = open(os.path.join(folder_name, "header.json"), "w")
        f.write(str(header))
        f.close()

        f = open(os.path.join(folder_name, "body.txt"), "w")
        f.write(body)
        f.close()

        for a in mail.attachments:
            print(a)
            dst =  folder_name = os.path.join("pybotlib_emails", mail.headers["Message-ID"].split("-")[1] +" " + mail_date, a["filename"])
            with open(dst, "w" ) as f:
                f.write(a["payload"].decode(a["content_transfer_encoding"]))
                f.close()
        return

def send_email_with_attachement(subject, body, sender_email, receiver_email, password, filename):

    """Sends a simple with one attachment from a gmail account.

    Args:
      subject(str): Subject of the email.

      body(str): Body of the email.

      sender_email(str): From field in the email.

      reciever_email(str): The recipient emaill address.

      password(str): Password of senders email.

      filename(str): Absoloute path of file to send in email or the file name if the file is in CWD.
    
    Returns:
      None.
    """


    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))


    # Open PDF file in binary mode
    with open(filename, "r") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        "attachment; filename= %s" %filename.split("\\")[-1],
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    if server.login(sender_email, password)[0] == 235:

        server.sendmail(sender_email, receiver_email, text)
        return
    else:
        print("Login Failed!")
        return

def send_HTML_email_with_attachement(subject, body, sender_email, receiver_email, password, filename, watermark="pybotlib RPA"):

    """Sends an visually pleasing HTML email with one attachment from a gmail account.

    Args:
      subject(str): Subject of the email.

      body(str): Body of the email.

      sender_email(str): From field in the email.

      reciever_email(str): The recipient emaill address.

      password(str): Password of senders email.

      filename(str): Absoloute path of file to send in email or the file name if the file is in CWD.
    
    Returns:
      None.
    """
    html = """
    <!doctype html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>pybotlib Transactional Email</title>
        <style>
        /* -------------------------------------
            INLINED WITH htmlemail.io/inline
        ------------------------------------- */
        /* -------------------------------------
            RESPONSIVE AND MOBILE FRIENDLY STYLES
        ------------------------------------- */
        @media only screen and (max-width: 620px) {
        table[class=body] h1 {
            font-size: 28px !important;
            margin-bottom: 10px !important;
        }
        table[class=body] p,
                table[class=body] ul,
                table[class=body] ol,
                table[class=body] td,
                table[class=body] span,
                table[class=body] a {
            font-size: 16px !important;
        }
        table[class=body] .wrapper,
                table[class=body] .article {
            padding: 10px !important;
        }
        table[class=body] .content {
            padding: 0 !important;
        }
        table[class=body] .container {
            padding: 0 !important;
            width: 100% !important;
        }
        table[class=body] .main {
            border-left-width: 0 !important;
            border-radius: 0 !important;
            border-right-width: 0 !important;
        }
        table[class=body] .btn table {
            width: 100% !important;
        }
        table[class=body] .btn a {
            width: 100% !important;
        }
        table[class=body] .img-responsive {
            height: auto !important;
            max-width: 100% !important;
            width: auto !important;
        }
        }

        /* -------------------------------------
            PRESERVE THESE STYLES IN THE HEAD
        ------------------------------------- */
        @media all {
        .ExternalClass {
            width: 100%;
        }
        .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {
            line-height: 100%;
        }
        .apple-link a {
            color: inherit !important;
            font-family: inherit !important;
            font-size: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
            text-decoration: none !important;
        }
        .btn-primary table td:hover {
            background-color: #34495e !important;
        }
        .btn-primary a:hover {
            background-color: #34495e !important;
            border-color: #34495e !important;
        }
        }
        </style>
    </head>
    <body class="" style="background-color: #f6f6f6; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
        <table border="0" cellpadding="0" cellspacing="0" class="body" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background-color: #f6f6f6;">
        <tr>
            <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
            <td class="container" style="font-family: sans-serif; font-size: 14px; vertical-align: top; display: block; Margin: 0 auto; max-width: 580px; padding: 10px; width: 580px;">
            <div class="content" style="box-sizing: border-box; display: block; Margin: 0 auto; max-width: 580px; padding: 10px;">

                <!-- START CENTERED WHITE CONTAINER -->
                <table class="main" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background: #ffffff; border-radius: 3px;">

                <!-- START MAIN CONTENT AREA -->
                <tr>
                    <td class="wrapper" style="font-family: sans-serif; font-size: 14px; vertical-align: top; box-sizing: border-box; padding: 20px;">
                    <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                        <tr>
                        <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">
                            <p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;">Hi %RECIPIENT%,</p>
                            <p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;"> %MESSAGE% </p>
                                </td>
                                </tr>
                            </tbody>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>

                <!-- END MAIN CONTENT AREA -->
                </table>

                <!-- START FOOTER -->
                <div class="footer" style="clear: both; Margin-top: 10px; text-align: center; width: 100%;">
                <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                    <tr>
                    <td class="content-block" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;">
                        <span class="apple-link" style="color: #999999; font-size: 12px; text-align: center;"> %WATERMARK% </span>

                    </td>
                    </tr>
                    <tr>
                    <td class="content-block powered-by" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;">
                        <a href="http://htmlemail.io" style="color: #999999; font-size: 12px; text-align: center; text-decoration: none;"></a>.
                    </td>
                    </tr>
                </table>
                </div>
                <!-- END FOOTER -->

            <!-- END CENTERED WHITE CONTAINER -->
            </div>
            </td>
            <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
        </tr>
        </table>
    </body>
    </html>
    """.replace("%MESSAGE%", body).replace("%RECIPIENT%", receiver_email.split("@")[0]).replace("%WATERMARK%", watermark)

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(html, "html"))


    # Open PDF file in binary mode
    with open(filename, "r") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        "attachment; filename= %s" %filename.split("\\")[-1],
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    if server.login(sender_email, password)[0] == 235:

        server.sendmail(sender_email, receiver_email, text)
        return
    else:
        print("Login Failed!")
        return

def pandas_read_google_sheets(sheet_id):
    """Returns a pandas DataFrame from a spreadsheet in google sheets.
    Make sure the spreadsheet has a "view" link and only contains one tab of data.

    Args:
      sheet_id(str): Individual googlesheet ID extracted from URL with view access.

    Returns:
      pandas.DataFrame: A dataframe with the data from the googlesheets.
    """
    r = requests.get('https://docs.google.com/spreadsheets/d/%s/export?format=csv' % sheet_id)
    data = r.content
    df = read_csv(BytesIO(data))
    return df

def save_csv_from_googlesheets(service_file, sheet_url, filename):
    """Save a google sheets table to .csv with name filename.
    
    Needs JSON credentials file location, full google sheets URL and filename to be saved.
    Google Sheet must be shared with view access to service account listed in JSON credentials file under 'client_email'.

    Args:
      service_file(str): Path to the google credentials json service file.
      sheet_url(str): URL of the googlesheet to be downloaded.
      filename(str): Name of the csv file to be saved without the '.csv'.
      
    Returns:
      True. The csv was saved.

    Raises:
      Exception: If the function does not return True.
    """
    try:
    #authorization
        gc = pygsheets.authorize(service_file=service_file)
        # Open google sheets from URL
        sh = gc.open_by_url(sheet_url)
        #select the first sheet
        wks = sh[0]
        wks.export(filename = filename)
        return True
    except Exception as e:
        raise e


def create_minio_bucket(host_uri, minio_access_key, minio_secret_key, bucket_name):
    """Creates a minio bucket."""
    minioClient = Minio('%s:9000' % host_uri,
                    access_key= minio_access_key,
                    secret_key= minio_secret_key,
                    secure=False)
    try:
        minioClient.make_bucket(bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

def write_file_to_minio_bucket(host_uri, minio_access_key, minio_secret_key, bucket_name, filename):
    """Write a file to a minio bucket.

    Args:
      host_uri(str): URI to minio instance.
      minio_access_key(str): Access key.
      minio_secret_key(str): Secret key.
      bucket_name(str): Bucket name to save.
      filename(str): Name of file to save to bucket. Must be in CWD.

    Returns:
      None.

    Raises:
      Exception: If bucket does not exist or the file is not found.
    """
    if not os.path.exists("./%s" % filename):
        raise Exception("file must be in current working directory")
    else:
        minioClient = Minio('%s:9000' % host_uri,
                        access_key= minio_access_key,
                        secret_key= minio_secret_key,
                        secure=False)
        try:
            object = minioClient.fput_object(
                bucket_name=bucket_name, object_name=filename, file_path="./%s" % filename
            )
            # print("MINIO FILE WRITE COMPLETE!")
            # print(object)
        except Exception as e:
            raise e
