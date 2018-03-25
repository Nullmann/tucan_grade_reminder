Description
===================
This python-script checks tucan for new grades and writes an email if there are differences.

Dependancy
===================
This script only works with Python 3 and Pip 3.
<br> On Debian, `sudo apt-get install python3-pip` automatically installs python 3 alongside pip.
<br> -- If an error occurrs, it may be needed to install libxml2 for the lxml-module (Required for MechanicalSoup)

Installation
===================

* Rename `config-dist.py` to `config.py` and insert your credentials
* On Windows:
```
pip install MechanicalSoup
py -3 main.py
```
* On Linux:
```
sudo pip3 install MechanicalSoup
python3 main.py
```
Note, that if you want to run the script from a cronjob, absolute paths may be required.

Misc
===================
Special thanks to @davidgengebach for his TUCaN-Tools and 3 lines of code, which overcame the https-redirect-orgy: https://github.com/tucanlib/tucan-tools
