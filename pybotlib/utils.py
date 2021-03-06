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

def check_and_dl_chrome_driver():

    """
    Checks Windows 10 system for Chrome Driver for use in RPA Automation.
    If not found will download the most recent version form google servers.
    """

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
    """
    Parses out datetime from email msg format
    """
    return (
       datetime.fromtimestamp(
           time.mktime(
               email.utils.parsedate(t)
           )
       )
   )

def return_emails_from_IMAP(email_account, password, email_folder, search_term="ALL", url='imap.gmail.com'):

    """
    Used to search a specific IMAP email folder and return a list of individual mailparser.MailParser objects.
    Will return no values if the login, folder, or search fails. You can replace search_term with other fields such as "UnSeen" or "Seen".

    Parameters
    ----------
    email_account : str
        Email address to read inbox from.

    password: str
        Password for associated email_account.

    email_folder: str
        Which IMAP folder to return emails from.
    
    search_term: str, optional
        Term that is used to search in email folder. Defaults to all.
    
    url: str, optinal
        IMAP server url. Defaults to imap.gmail.com for use with google gmail accounts.

    Returns
    -------
    list
        a list of mailparser.MailParser objects

    Example:

    list_of_emails = return_emails_from_IMAP(
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

def save_emails_to_CWD(list_of_mails):
    """
    Takes as input a list of mailparser.MailParser objects and saves the emails to current working directory under a folder called pybotlib_emails.
    Headers and body are saved as individual txt files inside a folder named after the subject and date recieved.
    Attachements are also saved into said folder.

    Parameters
    ----------
    list_of_mails: list
        Takes a list of mailparser.MailParser objects.
    
    Returns
    -------
    This function will save email as individual folders containing headers.json, body.txt, and any attachments under the CWD/pybotlib_emails.


    Example:

    list_of_mails = [msg1, msg2, msg3]

    save_emails_to_CWD(list_of_mails)

    """


    if not os.path.exists("pybotlib_emails"):
        os.mkdir("pybotlib_emails")

    for mail in list_of_mails:

        if type(mail) != mailparser.mailparser.MailParser:
            print "save_emails_to_cwd ony takes in a list of mailparser.MailParser objects"
            return
        
        header = mail.headers_json
        body = mail.body
        mail_date = dt_parse(mail.Date).strftime("%m-%d-%Y %H.%M.%S")

        folder_name = "pybotlib_emails\\%s" % (mail.headers["Message-ID"].split("-")[1] +" "+mail_date)

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        f = open(folder_name +"\\header.json", "w")
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
        return

def send_email_with_attachement(subject, body, sender_email, receiver_email, password, filename):

    """
    Sends a simple with one attachment from a gmail account.

    Parameters
    ----------
    subject: str
        Subject of the email.

    body: str
        Body of the email.

    sender_email: str
        From field in the email.

    reciever_email: str
        The recipient emaill address.

    password: str
        Password of senders email.

    filename: str
        Absoloute path of file to send in email or the file name if the file is in CWD.
    
    Example:
    send_email_with_attachement(
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

def send_HTML_email_with_attachement(subject, body, sender_email, receiver_email, password, filename, watermark="pybotlib RPA"):   

    """
    Sends HTML formatted email.
    filename can be the filename if the file is in CWD, if not you can use absoloute path.}
    
    Parameters
    ----------
    subject: str
        Subject of the email.

    body: str
        Body of the email.

    sender_email: str
        From field in the email.

    reciever_email: str
        The recipient emaill address.

    password: str
        Password of senders email.
        
    filename: str
        Absoloute path of file to send in email or the file name if the file is in CWD.
    
    Example:
    send_email_with_attachement(
        subject="Hello",
        body="Hi, hello.",
        sender_email="me@gmail.com",
        receiver_email="you@you.com",
        password="pswd",
        filename="file.pdf"
        )
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
