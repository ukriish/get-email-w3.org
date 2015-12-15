# get-email-w3.org
A python script to get all the emails from w3.org email list into a file using beautifulsoup

To run this code first make sure you have beautifulsoup module installed, if not the run this on your linux machine `$ apt-get install python-bs4`. For further reference please visit [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)

- If you have the pickled list of urls then run the program using the following command `python scrapEmail.py <filename>`
- Else if you would like to generate the pickle file yourself run `python scrapEmail.py`

_Here just run `$ python scrapEmail.py MonthLinks.pkl`_

Once you run the python script you will have a folder (Eg - `2015Nov`) per month. Each folder will have a file with the same name as the folder, which contains aggregated details of all the emails, and the rest of the files having the email data based on the serial number (Eg -`001.tsv`).

- The email list file will have text seperator as `"` and field seperator as `\t`
- The email data file will have text seperator as `"` and fiel seperator as `*|*`
