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

print("Accessing TUCaN...")

browser.open("https://www.tucan.tu-darmstadt.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N000000000000001,-N000344,-Awelcome")
	
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

print("Saving table as html-file...")

# Save table with current date and time as an html-file in the current folder
path = os.path.dirname(os.path.abspath(__file__)) + '/'
filename = str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + '.html'
file = open(path + filename, 'w')

grade_table = browser.get_current_page().find_all('table')
grade_table = re.sub('N(\d*?)(,|\")', '', str(grade_table)) # Strip the table of these weird number which changes with each login
file.write(grade_table)
file.close()

# Get all html-files in the current folder, beginning with the current year
list_of_files = glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/*' + str(datetime.datetime.now().year) + '*.html')
list_of_files = sorted(list_of_files,key=os.path.getctime)

print("Comparing tables...")

# Check if there is more than one item
if (list_of_files.__len__() == 1):
    print("RESULT: There is no file stored to compare to (first time running?)")
else:
    # Get last grade-table for comparison
    with open(list_of_files[-2], 'r') as second_latest_file:
        prev_grade_table = second_latest_file.read()
    with open(list_of_files[-1], 'r') as latest_file:
        current_grade_table = latest_file.read()

    if (prev_grade_table == current_grade_table):
        print('RESULT: The two files are the same - No grades have changed and nothing needs to be done')
    else:
        print('RESULT: Sending E-Mail with changed grades...')
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
	
    if (CFG.REMOVE_OLD_FILES == 'yes'):
        print("Removing old files...")
        # Remove oldest file
        os.remove(list_of_files[0])
    else:
        print("Not removing old files")