from os import mkdir
from requests import get
from shutil import copy
import StringIO
from zipfile import ZipFile
from os.path import exists
import platform
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import mailparser as mailparser
import time
import os
import datetime
from datetime import datetime,timedelta

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

def dt_parse(t):
   return (
       datetime.fromtimestamp(
           time.mktime(
               email.utils.parsedate(t)
           )
       )
   )

def ReturnEmailsFromImap(email_account, password, email_folder, search_term="ALL", url='imap.gmail.com'):

    """
    Used to search a specific IMAP email folder and return a list of individual mailparser.MailParser objects.
    Will return no values if the login, folder, or search fails. You can replace search_term with other fields such as "UnSeen" or "Seen".

    Example:

    list_of_emails = ReturnEmailsFromImap(
        email_account="me@me.com",
        password="psw",
        email_folder="INBOX",
        search_term="ALL",
        url='imap.gmail.com')
    """

    M = imaplib.IMAP4_SSL(url)

    try:
        rv, data = M.login(email_account, password)
    except imaplib.IMAP4.error:
        print "Login Failed. Check Credentials and imap url."
        return
    
    rv, data = M.select(email_folder)

    if rv != 'OK':
        print "Email folder not found."
        return
    
    response = []
    rv, data = M.search(None, search_term)

    if rv != 'OK':
        print "No unSeen Messages"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            #return

        msg = email.message_from_string(data[0][1])
        parsed_msg = mailparser.parse_from_string(msg.as_string())
        response.append(parsed_msg)
    M.logout()
    return response

def SaveEmailsToCWD(list_of_mails):
    """
    Takes as input a list of mailparser.MailParser objects and saves the emails to current working directory under a folder called pybotlib_emails.
    Headers and body are saved as individual txt files inside a folder named after the subject and date recieved.
    Attachements are also saved into said folder.

    Example:

    list_of_mails = [msg1, msg2, msg3]

    SaveEmailsToCWD(list_of_mails)

    """
    
    if not os.path.exists("pybotlib_emails"):
        os.mkdir("pybotlib_emails")

    for mail in list_of_mails:

        if type(mail) != mailparser.mailparser.MailParser:
            print "save_emails_to_cwd ony takes in a list of mailparser.MailParser objects"
            return
        
        header = mail.headers
        body = mail.body
        mail_date = dt_parse(mail.Date).strftime("%m-%d-%Y %H.%M.%S")

        folder_name = "pybotlib_emails\\%s" % (mail.headers["Subject"]+" "+mail_date)

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        f = open(folder_name +"\\header.txt", "w")
        f.write(str(header))
        f.close()

        f = open(folder_name + "\\body.txt", "w")
        f.write(body)
        f.close()

        for a in mail.attachments:
            print(a)
            with open(folder_name + "\%s" % a["filename"], "w" ) as f:
                f.write(a["payload"].decode(a["content_transfer_encoding"]))
                f.close()

def SendEmailWithAttachment(subject, body, sender_email, receiver_email, password, filename):

    """
    Sends a simple with one attachment from a gmail account.

    Example:
    SendEmailWithAttachment(
        subject="Hello",
        body="Hi, hello.",
        sender_email="me@gmail.com",
        receiver_email="you@you.com",
        password="pswd",
        filename="file.pdf"
        )
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
