from bs4 import BeautifulSoup
import urllib2

#quote_page = 'http://www.google.de'
quote_page = 'https://www.uhrzeit123.de/'
page = urllib2.urlopen(quote_page)

soup = BeautifulSoup(page, 'html.parser')

#print soup.prettify().encode('utf-8')
#for finding in soup.find_all('a'):
#    print finding.text#.encode('utf-8')

#print str(soup.find('time_hour')) + ":" + str(soup.find('time_min')) + ":" + str(soup.find('time_sec'))

hour = soup.find("span", {"class" : "time_hour"}).text
minute = soup.find("span", {"class" : "time_min"}).text
second = soup.find("span", {"class" : "time_sec"}).text

print "Aktuelle Zeit: " + hour + ":" + minute + ":" + second