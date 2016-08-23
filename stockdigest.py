# TODO put file header information here

# download stock data from yahoo
import os
import sys
from pandas.io.data import get_data_yahoo
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import StringIO
import urllib

# E-Mail
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import mimetypes
import smtplib

# get news data from google finance feed (feedparser)
import feedparser



#get config variables
import config



# functions
def get_stock_graph(data):
	data.plot(subplots = True, figsize= (8, 4))
	plt.legend(loc = 'best')
	#plt.show()
	fig = plt.gcf()
	imgdata = StringIO.StringIO()
	fig.savefig("image.png")

def get_google_news(ticker):
	# split symbol in case of notation for yahoo, like GOOG.DE
	head, sep, tail = ticker.partition('.')
	# get news data from google finance feed (feedparser)
	rss_url = 'https://www.google.com/finance/company_news?output=rss&q=' + head
	d = feedparser.parse(rss_url)
	news = '<br> News: <br><ul>' 
	for post in d.entries:
		news += '<li><a href="' + post.link + '">' + post.title + "</a></li>"
	news += '</ul>'
	return news

def pct_change(data):
	# calculate percent change for given timespan
	pct = 100 * (( data['Close'].iloc[len(data)-1] / data['Close'].iloc[0] ) -1)
	pct = "%.2f" % (pct)
	return pct	

# get start and end days
end = datetime.today()
start = end - timedelta(config.timespan)

for ticker in config.tickers:
	#fetch stock data from yahoo 
	data = get_data_yahoo(ticker, start, end)[['Close']] # We just need Close for now
	#save image for later (image.png) TODO: Put in tmp directory
	get_stock_graph(data)
	
	# Compose  Email
	pct = pct_change(data) + '%'
	if pct[0] != '-':
		pct = '+' + pct


	email_subject = 'Stock update for ' + ticker + ': ' + pct
	email_body = '' 

	email_body += ticker + ' gained <strong>' + pct + '</strong> in the last ' + str(config.timespan) + ' Days! <br>'

	email_body += '<img src="cid:image1"><br><br>'

	email_body += get_google_news(ticker)

	# Send Email
	# Create the root message and fill in the from, to, and subject headers
	msgRoot = MIMEMultipart('related')
	msgRoot['Subject'] = email_subject
	msgRoot['From'] = config.email_from
	msgRoot['To'] = config.email_to
	msgRoot.preamble = 'This is a multi-part message in MIME format.'

	# Encapsulate the plain and HTML versions of the message body in an
	# 'alternative' part, so message agents can decide which they want to display.
	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	msgText = MIMEText('Please view message as HTML.')
	msgAlternative.attach(msgText)

	# We reference the image in the IMG SRC attribute by the ID we give it below
	msgText = MIMEText(email_body, 'html')
	msgAlternative.attach(msgText)

	# This example assumes the image is in the current directory
	fp = open('image.png', 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()

	# Define the image's ID as referenced above
	msgImage.add_header('Content-ID', '<image1>')
	msgRoot.attach(msgImage)


	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(config.email_username,config.email_password)
	server.sendmail(config.email_from, config.email_to, msgRoot.as_string())
	server.quit()
















