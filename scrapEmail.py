
import sys
from multiprocessing.dummy import Pool as ThreadPool 
import os.path
import pickle
import urllib2
import codecs
import unicodedata
from bs4 import BeautifulSoup, Comment

def getMsgHeader(soup):
	''' Extract the header details like From, To, Message-Id and Date'''
	msgHeader = {'From':'', 'To':'', 'Message-Id':'','Date':'', 'Cc':'' }
	for span in soup:
		if span.dfn.contents[0] == 'From' or span.dfn.contents[0] == 'FROM':
			pass
			try:
				msgHeader['From'] = span.find('a').contents[0]
			except:
				pass
		elif span.dfn.contents[0] == 'To' or span.dfn.contents[0] == 'TO' :
			try:
				toCS = ''
				for tags in span.findAll('a'):
					toCS += tags.text + ';'
				msgHeader['To'] = toCS
			except:
				pass
		elif span.dfn.contents[0] == 'Cc' or span.dfn.contents[0] == 'CC' :
			try:
				ccCS = ''
				for tags in span.findAll('a'):
					ccCS += tags.text + ';'
				msgHeader['Cc'] = ccCS
			except:
				pass				
		elif span.dfn.contents[0] == 'Message-Id' or span.dfn.contents[0] == 'Message-ID':
			try:
				msgHeader['Message-Id'] = span.contents[1].strip(':').strip().rstrip('>').lstrip('<')
			except:
				pass
		elif span.dfn.contents[0] == 'Date' or span.dfn.contents[0] == 'DATE':
			try:
				msgHeader['Date'] = span.contents[1].strip(':').strip()
			except:
				pass
	return msgHeader

def getMsgBody(soup):
	''' Extract the email content'''
	msgBody = ''
	for tags in soup.findAll('pre'):
		msgBody += tags.text
	return msgBody.strip()

def getMsgSubject(soup):
	''' Extract the subject line'''
	return soup.string.strip()

def getInReplyTo(soup):
	''' Extract the in reply to message id'''
	inReplyTo = ''
	for comment in soup.findAll(text=lambda text:isinstance(text, Comment)):
		if comment.find('inreplyto') > 0:
			#strip blank spaces and the variable and replace the &#64 with @
			inReplyTo = comment.strip().rstrip('"').lstrip('inreplyto="').replace('&#64;','@')
	return inReplyTo

def getMailDetailsToFile(urls):
	''' Load the page and extract all the required details'''
	fileName = urls[0].split('/')[6].strip()
	if not os.path.exists(fileName + '.csv'):
		print 'Writing to file : ' + fileName
		fileMonth = codecs.open( fileName + '.csv', 'w', 'utf-8')
		fileMonth.write('Message-Id\tDate\tFrom\tTo\tSubject\tBody\tIn Reply To\n')
		for url in urls:	
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html, 'html.parser')
			#Get Message subject
			msgSub = getMsgSubject(soup.h1)
			#Get the in reply to
			inReplyTo = getInReplyTo(soup)
			#From the div class mail get the span elements to fetch the header and mail body
			for tags in soup.find_all('div', class_='mail'):
				msgHeader = getMsgHeader(tags.find_all('span'))
				msgBody = getMsgBody(tags)
			print 'Writing contents of ' + url + ' to file' #notification to terminal
			#write to file
			fileMonth.write(msgHeader['Message-Id'] + '\t' + msgHeader['Date'] + '\t' + msgHeader['From'] + '\t' + msgHeader['To'] + '\t' + msgSub + '\t' + msgBody + '\t' + inReplyTo + '\n')
		fileMonth.close()
	else:
		print 'File already exits'

def getMailUrls(urls):
	''' Get all the mail links from the monthly mail page'''
	if not urls:
		return []
	else:
		print 'Fetching mail urls from ' + urls[0]
		html = urllib2.urlopen(urls[0]).read()
		soup = BeautifulSoup(html, 'html.parser')
		urlList = []
		for tags in soup.find_all('div', class_='messages-list'):
			for anchors in tags.find_all('a'):
				#extract the link
				partialUrl = anchors.get('href')
				if partialUrl:
					#append it with the original url
					urlList.append(urls[0].replace('thread.html', partialUrl))
		return [urlList] + getMailUrls(urls[1:])

def getSortedOnThredUrls(urls):
	''' Return the thread sorted page'''
	return filter(lambda x: x.find('thread.html') > 0, urls)

def getNotSortedUrls(urls):
	''' Return the normal non sorted page only'''
	return filter(lambda x: x.find('thread') < 0 and x.find('author') < 0 and x.find('subject') < 0, urls)

def getAllUrls(soup, mainUrl):
	''' Fetch all the urls '''
	fullUrls = []
	for month in soup.find_all('tbody'):
		for partialUrl in month.find_all('a'):
			fullUrls.append(mainUrl + partialUrl.get('href'))
	return fullUrls

def writeUrlListToFile():
	''' Get all the links a pickle it to be used later'''
	pickleFile = 'MonthLinks.pkl'
	textFile = 'MonthLinks.txt'
	fileP = open(pickleFile, 'wb')
	fileTxt = codecs.open(textFile, 'w', 'utf-8')
	mainUrl = 'https://lists.w3.org/Archives/Public/public-html/'
	html = urllib2.urlopen(mainUrl).read()
	soup = BeautifulSoup(html, 'html.parser')
	allUrls = getAllUrls(soup, mainUrl)
	threadUrls =  getSortedOnThredUrls(allUrls)
	mailUrls = getMailUrls(threadUrls)
	for urls in mailUrls:
		pickle.dump(urls, fileP, -1)
		for url in urls:
			fileTxt.write(url.strip() + '\n')
	fileTxt.close()
	fileP.close()
	return pickleFile

def processLinksFrom(pickleFile):
	''' Get data from pickle and get mails'''
	fileP = open(pickleFile, 'rb')
	mailUrls = []
	while 1:
	    try:
	        mailUrls.append(pickle.load(fileP))
	    except:
	        break
	fileP.close()
	#Create a multiple threads and get details
	pool = ThreadPool(5)
	results = pool.map(getMailDetailsToFile, mailUrls)
	pool.close()
	pool.join()

def main(fileName):
	if len(fileName) == 0:
		processLinksFrom(writeUrlListToFile())
	elif len(fileName) == 1:
		if os.path.exists(fileName[0]):
			processLinksFrom(fileName[0])
	else:
		print "Please try again : $ python scrapEmail.py or $ python scrapEmail.py <filename>"

if __name__ == '__main__':
    main(sys.argv[1:])
