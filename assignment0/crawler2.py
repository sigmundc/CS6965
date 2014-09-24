from urlparse import urlparse
import urllib2
from bs4 import BeautifulSoup
from Queue import Queue
import robotparser
import time
import sys
import tldextract

# seed = 'http://www.cs.utah.edu'
seed = raw_input('Enter the seed url: ')
if seed is None or len(seed) == 0:
	sys.exit("Please enter a valid seed url.")
domain = urlparse(seed)
assert all([domain.scheme, domain.netloc])
assert domain.scheme in ['https', 'http', 'ftp']
# seed_domain = domain.netloc
seed_domain= tldextract.extract(seed).domain

focused = ''

urls = Queue()
urls.put(seed)
visited = []
skipped = []

# Handle robots.txt
rp = robotparser.RobotFileParser()
rp.set_url(seed + "/robots.txt")
rp.read()

while urls.qsize() != 0:
	url = urls.get()
	if (url in visited):
		continue	
	if not rp.can_fetch("*", url):
		print "Skipping '{0}' ...".format(url)
		skipped.append(url)
		continue
	print "Crawling '{0}' ...".format(url)

	try:
		response = urllib2.urlopen(url)
		page_source = response.read()
		# page_source = page_source.decode('utf-8')
		# keep track of visited urls
		visited.append(url)

		soup = BeautifulSoup(page_source, from_encoding='utf-8')

		for link in soup.find_all('a'):
			new_link = link.get('href')
			print link.get('title')
			if new_link is None:
				continue
			if (len(new_link) > 0 and new_link[0] == '/'):
				new_link = seed + new_link
			new_link = new_link.strip('/') # making sure www.cs.utah.edu and www.cs.utah.edu/ are both the same

			# limit page crawling within a given Web domain
			# new_link_domain = urlparse(new_link).netloc
			new_link_domain = tldextract.extract(new_link).domain
			if (new_link_domain == seed_domain
				and	new_link not in visited):
				if len(focused) > 0: # for basic focused crawling
					if focused in new_link:
						urls.put(new_link)
				else:
					urls.put(new_link)
				# print link.text + " - " + new_link
		# print list(urls.queue)
		print "Visited: {0}".format(visited)
		print "Skipped: {0}".format(skipped)
		print "\n"
		# break
	except:
		print "Unexpected error:", sys.exc_info()[0]

	# politeness measures
	time.sleep(3)

