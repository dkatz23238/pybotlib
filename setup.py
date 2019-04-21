from setuptools import setup

#str
long_desc = """
.. figure:: https://github.com/dkatz23238/pybotlib/raw/master/img/pybotlib.png
   :alt: pybotlib-image

   pybotlib-image
What is pybotlib?
=================

pybotlib is a high level library for creating business oriented Robotic
Process Automations using Python.

This branch is developed for Python 3.7+ and Linux/Ubuntu.

This specific branch has been optimized and tested to run on an Ubuntu
desktop client. It can run on other Linux enviornments.

For the windows version of pybotlib check out the master branch.

Aimed at outperforming and outcosting closed sourced solutions such as
Automation Anywhere or Blueprism, pybotlib consists of a central wrapper
around the selenium webdriver exposing highly customized methods and
functions through an efficient and easy to use API.

The package's goal is to facilitate the RPA development process and
bring Python into the Intelligent Automation and Robotic Process
Automation industries.

Some conveniences provided are:

-  Robust methods to navigate business applications frontends oriented
   towards efficiently managing large scale Automation endeavors

-  RPA logging locally hosted or integrated with Google Cloud
   StackDriver (coming soon)

-  Integration with SAP scripting client (coming soon) (Windows only)
-  Documentation and examples to create robust enterprise grade RPAs
   using python

-  Integration with major platforms for task specific business
   automaions

Getting Started
---------------

0) If you are using this branch you can pip install pybotlib from PyPI
   by running the following command:

::

    python -m pip install pybotlib

2) Make sure that Mozilla Firefox is installed on the host machine. Run
   the provied batch script to install the geckodriver needed to
   automate web activities.

::

    python -c "from pybotlib.utils import get_geckodriver; get_geckodriver();"

3) You are now ready to use the package. Import the VirtualAgent class
   with the following code:

.. code:: py

    from pybotlib import *

Example pybotlib RPA following best practices
---------------------------------------------

I have provided an example robot named investigator\_RPA.py. This RPA
will read a table with company names and download official financial
reports from the Securitiy and Exchanges Comission website. It a simple
robot teared down to the bear minimum in order to exemplify how to best
use pybotlin and also how to decouple the business input and output data
from the RPA itself. The input data for this RPA is just a googlesheets
I have hosted with a few comapany names and can be found
`here <https://docs.google.com/spreadsheets/d/1pBecz5Db9eK0QDR_oePmamdaFtEiCaO69RaE-Ozduko/edit?usp=sharing>`__.

The output data is programmed to be sent to a Minio file server you can
run one locally or use your own and change the env variables in
env-var.sh

Run a minio file server on localhost via following command to persist
RPA output data. The keys are accessed to the RPA via the env variables:

::

    mkdir -p $HOME/tmp && cd $HOME/tmp
    mkdir -p data
    docker run -d  -p 9000:9000 -e "MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE" -e "MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" minio/minio server /data

Then follow the steps from Getting Started and run the RPA with
following commands:

::

    bash run_RPA.sh

The example RPA follows a few simple rules that are recomended to be
folowed:

0. Sensitive and dynamic data in the form of key values pairs that the
   RPA may use to access various systems should be stored in enviornment
   variables and be accessed via the ``os.environ`` method in python.

1. Business input and output data should be decoupled from the RPA
   itself. The system I recomend to use for data persistance is using
   cloud file storage providers or hosting your own. Minio is a great
   self hosted cloud file storage system that you can easily deploy with
   one simple command. The example RPA needs an active running Minio
   server up and running, all of the variables needed to access the
   minio server are stored in env-vars.sh.

2. All execution of RPA should be handled by single bash script called
   run\_RPA.sh and should be able to run without sudo.

Quick Start
-----------

To create an instance of an active RPA we must instantiate the
VirtualAgent class. The instance will be the central object in our
workflow and process automation.

.. code:: py

    human_resources_bot = VirtualAgent(
      bot_name="EDGAR_investigator_bot",
            downloads_directory=os.path.join(os.getcwd(), "bot_downloads"),
            firefoxProfile="/home/$USER/.mozilla/firefox"
      )

    human_resources_bot.create_log_file()
    human_resources_bot.initialize_driver()
    human_resources_bot.log("WebDriver Initiated")

A common issue in process automation is being able to efficiently
identify specific elements within an html front end.

Ideally this should be done with the least lines of code possible.

This is why we have created the find\_by\_tag\_and\_attr method that
iterates through every single element of a specific tag on a page and
evaluates if any of the elements attributes matches the evaluation
string provided. Matched elements are returned in a list.

.. code:: py

    my_robot = VirtualAgent(bot_name="my_robot", downloads_directory="my_robot_downloads_folder")
    my_robot.find_by_tag_and_attr(tag, attribute, evaluation_string, sleep_secs)

Logging and RPA Auditability
----------------------------

When developing RPAs you usually want to be able to log two different
types of events: execution logs and transactional logs. Transactional
logs give information about the process you are automating while the
execution log provides information on the specific run of an RPA.

Pybotlib creates a folder called pybotlib\_logs under the current User's
directory. Every RPA has the ability to create and automatically write
to its logfile. The log file is CSV file, an example for illustrative
purposes is provided below:

+-------+----------------------------+---------------+------------------------------+-------------------------+
| idx   | message                    | tag           | timestamp                    | tz                      |
+=======+============================+===============+==============================+=========================+
| 0     | start                      | execution     | 2019-01-11 11:44:01.399000   | Pacific Standard Time   |
+-------+----------------------------+---------------+------------------------------+-------------------------+
| 1     | searching edgar for AAPL   | transaction   | 2019-01-11 11:44:06.216000   | Pacific Standard Time   |
+-------+----------------------------+---------------+------------------------------+-------------------------+
| 2     | ...                        | ...           | ...                          | ...                     |
+-------+----------------------------+---------------+------------------------------+-------------------------+

``VirtualAgent.create_log_file()`` will create the csv used to audit the
execution of an RPA. Will also create the first row in log file to
signal bot start.

``VirtualAgent.log(message)`` will directly log a transaction tagged
message to the current file.

``VirtualAgent.log(message, tag=TAG)`` allows users to customize tags

``VirtualAgent.log_bot_completion()`` will log a message "end" to the
log file tagged as execution.

Documentation
-------------

Docs coming soon. Stay tuned or sign up for our mailing list *here*

License
-------

This project is licensed under the MIT License - see the
`LICENSE.md <LICENSE.md>`__ file for details

Acknowledgments
---------------

-  Thanks to @AlSweigart for inspiring this package


"""
#list
install_reqs = [
 'numpy',
 'selenium',
 'pandas',
 'requests',
 'lxml',
 'html5lib',
 'xlrd',
 'openpyxl',
 'mail-parser',
 'pygsheets',
 'minio',
 'BeautifulSoup4',
 'python3-xlib',
 'Xlib',
 'PyAutoGUI==0.9.39'
 ]




setup(
    name="pybotlib",
    version="0.1.4",
    description="Object oriented python RPA library",
    license="MIT",
    long_description=long_desc,
    author="David Katz",
    python_requires='>3.7',
    author_email="davidemmanuelkatz@gmail.com",
    url="https://github.com/dkatz23238/pybotlib/tree/ubuntu-client-37",
    packages=["pybotlib", "pybotlib.exceptions", "pybotlib.utils"],
    install_requires=install_reqs,
    classifiers=['Operating System :: POSIX',]
)
