
![pybotlib-image](/img/pybotlib.png)

# What is ```pybotlib```?
```pybotlib``` is a high level library for creating business oriented Robotic Process Automations using Python 2.7.15.
The master branch of pybotlib is developed to run on Windows 10.
In order to use pybotlib with Linux refer to the ubuntu-client branch.

Aimed at outperforming and outcosting closed sourced solutions such as Automation Anywhere or Blueprism, ```pybotlib``` consists of a central wrapper around the selenium webdriver exposing highly customized methods and functions through an efficient and easy to use API.

The package's goal is to facilitate the RPA development process and bring Python into the Intelligent Automation and Robotic Process Automation industries.

Some conveniences  provided are:

 - Robust methods to navigate business applications frontends oriented towards efficiently managing large scale Automation endeavors

 - RPA logging locally hosted or integrated with Google Cloud StackDriver (coming soon)

 - Documentation and examples to create robust enterprise grade RPAs using python

 - Integration with major platforms for task specific business process automation

Features that are in development:
 - Integration with SAP scripting client 
 - Logging with GCP StackDriver
 - Integrations with Google Drive

## 👨🏻‍💻 Installation

 1. First download or clone the repository and cd into the directory. Make sure Python27 is installed.

 2. Install necessary packages by running the pip command with provided requirements.txt file:

    ```
    pip install -r requirements.txt
    ```

3. Make sure Google Chrome is installed on the host machine. Be prepared to run the check_and_dl_chrome_driver function provided in the library in order to download the most recent chrome webdriver for process automation. Running the following code will download the latest chromedriver and .crx extensions:

    ```
    from pybotlib.utils import check_and_dl_chrome_driver
    # Checks if Google Chrome Driver is found on machine. Downloads if needed.
    check_and_dl_chrome_driver()
    ```

4. You are now ready to use the package. Import the VirtualAgent class with the following code:

    ```
    from pybotlib import *
    ```

## 🤖Example Robot

I have provided an example robot named investigator_RPA.py. This bot will lookup relevant news articles for specific topics provided in a list. Once completed all the steps above run the following lines of code to execute the robot. Feel free to edit and customize the robot on your machine!

```
python investigator_RPA.py
```

## ⚙️ Developing custom RPA's

To create an instance of an active RPA we must instantiate the VirtualAgent class. The instance will be the central object in our workflow and process automation.


```
human_resources_bot = VirtualAgent(bot_name="HR_bot", downloads_directory="timesheets")
human_resources_bot.create_log_file()
human_resources_bot.initialize_driver()
human_resources_bot.log("WebDriver Initiated")
```

A common issue in process automation is being able to efficiently identify specific elements within an html front end.

Ideally this should be done with the least lines of code possible.

This is why we have created the find_by_tag_and_attr method that iterates through every single element of a specific tag on a page and evaluates if any of the elements attributes matches the evaluation string provided. Matched elements are returned in a list.

```
my_robot = VirtualAgent(bot_name="my_robot", downloads_directory="my_robot_downloads_folder")
my_robot.find_by_tag_and_attr(tag, attribute, evaluation_string, sleep_secs)
```

## 👁‍🗨 Logging and RPA Auditability

When developing RPAs you usually want to be able to log two different types of events: execution logs and transactional logs. Transactional logs give information about the process you are automating while the execution log provides information on the specific run of an RPA.

Pybotlib creates a folder called pybotlib_logs under the current User's directory. Every RPA has the ability to create and automatically write to its logfile. The log file is CSV file, an example for illustrative purposes is provided below:

| idx | message                  | tag         | timestamp                  | tz                    |
|-----|--------------------------|-------------|----------------------------|-----------------------|
| 0   | start                    | execution   | 2019-01-11 11:44:01.399000 | Pacific Standard Time |
| 1   | searching edgar for AAPL | transaction | 2019-01-11 11:44:06.216000 | Pacific Standard Time |
| 2   | ...                      | ...         | ...                        | ...                   |

```VirtualAgent.create_log_file()``` will create the csv used to audit the execution of an RPA. Will also create the first row in log file to signal bot start.

```VirtualAgent.log(message)``` will directly log a transaction tagged message to the current file.

```VirtualAgent.log(message, tag=TAG)``` allows users to customize tags

```VirtualAgent.log_bot_completion()``` will log a message "end" to the log file tagged as execution.

## 📜 Documentation

Docs coming soon. Stay tuned or sign up for our mailing list *here*

## 📃 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## 📚 Acknowledgments

* Thanks to @AlSweigart for inspiring this package. After I read his free ebook I was inspired to take his work to the next level and start developing a stack of products for enterprise grade RPA development. ```pybotlib``` is the first of many
