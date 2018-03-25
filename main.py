#! python
# -*- coding: utf-8 -*-

import sys
print("Python version: " + sys.version)

import mechanicalsoup  # Automatic interaction with websites. Substitutes mechanize for Python 2.x
import datetime
import re # For regular expressions
# For manipulation of OS files
import glob
import os
# To send the mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Import config-file
import config as CFG

# Connect to site
browser = mechanicalsoup.StatefulBrowser()
# browser.set_verbose(2)  # shows URL for each visited site
# browser.set_debug(True);  # Opens Browser if there is an error
browser.open(
    "https://www.tucan.tu-darmstadt.de/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N000000000000001,-N000344,-Awelcome")

# Fill-in the search form
browser.select_form('#cn_loginForm')  # CSS-Selektor
browser["usrname"] = CFG.TU_ID
browser["pass"] = CFG.TU_ID_PASSWORD
response = browser.submit_selected()

# Thanks to @davidgengenbach for the next three lines of code (damned redirects!)
redirected_url = "=".join(response.headers['REFRESH'].split('=')[1:])
start_page = browser.open('https://www.tucan.tu-darmstadt.de' + redirected_url)
browser.open('https://www.tucan.tu-darmstadt.de' + start_page.soup.select('a')[2].attrs['href'])

# Navigate to "Module results" page
browser.follow_link(browser.find_link(url_regex='PRGNAME=COURSERESULTS'))

# Save table with current date and time
file = open(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace(':', '-') + '.html', 'w')

grade_table = str(browser.get_current_page().find_all('table'))

# Strip the table of these weird number which changes with each login
grade_table = re.sub('N(\d*?)(,|\")', '', grade_table)
file.write(grade_table)
file.close()

# Get all html-files in the current folder, beginning with the current year
list_of_files = glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/*' + str(datetime.datetime.now().year) + '*.html')

# Check if there is more than one item
if (list_of_files.__len__() == 1):
    print("SKIPPING COMPARISON: There is no file stored to compare to (first time running?)")
else:
    # Get last grade-table for comparison
    with open(max(list_of_files[:-1], key=os.path.getctime), 'r') as second_latest_file:
        prev_grade_table = second_latest_file.read()

    with open(max(list_of_files, key=os.path.getctime), 'r') as latest_file:
        current_grade_table = latest_file.read()

    if (prev_grade_table == current_grade_table):
        print('The two files are the same - No grades have changed and nothing needs to be done anymore')
    else:

        print('Send E-Mail with changed grades')
        msg = MIMEMultipart()
        msg['From'] = CFG.FROM_MAIL
        msg['To'] = CFG.TO_MAIL
        msg['Subject'] = "Automatic Mail: There is a new grade in TUCaN"
        msg.attach(MIMEText(current_grade_table, 'html'))

        server = smtplib.SMTP(CFG.SMTP_ADDRESS, CFG.SMTP_PORT)

        server.starttls()
        server.login(CFG.FROM_MAIL, CFG.FROM_MAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(CFG.FROM_MAIL, CFG.TO_MAIL, text)
        server.quit()

# ToDo: Upload to Github (find name + readme.MD [USE ATOM MARKDOWN PLUGIN])
## Pip install mechanical soup
## Thank David Gengebach
## Requirement: python 3
## config als gitignore
### config-dist
# ToDo: Set hourly cronjob on Raspi
