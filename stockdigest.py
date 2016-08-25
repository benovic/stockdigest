# TODO put file header information here

# download stock data from yahoo
import os
import sys

# google intraday data things
import pandas_datareader.data as web
import pandas as pd
import requests


from pandas.io.data import get_data_yahoo
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
# from matplotlib.finance import candlestick, candlestick2, candlestick2_ohlc
import matplotlib.dates as mdates
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
def get_stock_graph(data, ticker):
	plt.style.use('ggplot')
	data.plot(x='Datetime',y='Close', figsize= (15, 4), title=ticker)
	plt.savefig("image.png")
	#plt.show()

def get_google_news(ticker):
	# get news data from google finance feed (feedparser)
	rss_url = 'https://www.google.com/finance/company_news?output=rss&q=' + ticker
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

def get_intraday_data(symbol, exchange, interval_seconds=301, num_days=10):
	# Specify URL string based on function inputs.
	url_string = 'http://www.google.com/finance/getprices?q={0}'.format(symbol.upper())
	url_string += '&x=' + exchange # to include other exchanges
	url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds,num_days)
	# Request the text, and split by each line
	r = requests.get(url_string).text.split()
	# Split each line by a comma, starting at the 8th line
	r = [line.split(',') for line in r[8:]]
	# Save data in Pandas DataFrame
	df = pd.DataFrame(r, columns=['Datetime','Close','High','Low','Open','Volume'])

	# Convert UNIX to Datetime format
	df['Datetime'] = df['Datetime'].apply(lambda x: datetime.fromtimestamp(int(x[1:])))
	# Convert to floats
	df['Open'] = df['Open'].apply(lambda x: float(x))
	df['Close'] = df['Close'].apply(lambda x: float(x))

	return df

# get start and end days
end = datetime.today()
start = end - timedelta(config.timespan)



for ticker in config.tickers:
	# split symbol in case of notation for yahoo, like GOOG.DE
	exchange, sep, symbol = ticker.partition(':')
	
	# fetch stock data from google
	data = get_intraday_data(symbol,exchange, 301, config.timespan)
	#safe chart as image
	get_stock_graph(data, ticker)
	
	# get google News
	google_news = get_google_news(ticker)
	
	# get relative change percent for timespan
	pct = pct_change(data) + '%'
	if pct[0] != '-':
		pct = '+' + pct
	
	# Compose  Email
	


	email_subject = 'Stock update for ' + ticker + ': ' + pct
	email_body = '' 

	email_body += ticker + ' gained <strong>' + pct + '</strong> in the last ' + str(config.timespan) + ' Days! <br>'

	email_body += '<img src="cid:image1"><br><br>'

	email_body += google_news

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
















