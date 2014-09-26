from urlparse import urlparse
import urllib2
from bs4 import BeautifulSoup
from Queue import Queue
import robotparser
import time
import sys
import tldextract
import urlnorm

def normalize_url(base_url, url):
	myfile3 = open('normalization_log', 'a')
	myfile3.write("base url:{0}\n".format(base_url))
	myfile3.write("url:{0}\n".format(url))
	myfile3.close()
	result = ''

	# if url starts with http:// or https://
	allowed_scheme = ['http', 'https']
	url_scheme = urlparse(url).scheme
	if url_scheme in allowed_scheme:
		return urlnorm.norm(url)
	elif url_scheme == 'mailto':
		return False
	elif len(url_scheme) == 0:
		# check if URL starts with ../
		if (url[:3] == '../') or (url[:2] == './'):
			return urlnorm.norm(base_url+'/'+url)
		elif url[0] == '/': # e.g. /page/page
			# That means it's the domain + url
			url_obj = urlparse(base_url)
			new_url = url_obj.scheme + "://" + url_obj.netloc + url
			return urlnorm.norm(new_url)

		else: # URL should be just html page e.g. research.html
			# so we need to replace the last part
			# if URL is 'http://www.test.com/page/page/12345':
			# results will be ['http://www.test.com/page/page', '12345']
			parts = base_url.rsplit('/', 1)
			return urlnorm.norm(parts[0]+'/'+url)
	result = url
	return result

# seed = 'http://www.cs.utah.edu'
seed = raw_input('Enter the seed url: ')
if seed is None or len(seed) == 0:
	sys.exit("Please enter a valid seed url.")
# normalize seed
seed = normalize_url('',seed)
domain = urlparse(seed)
assert all([domain.scheme, domain.netloc])
assert domain.scheme in ['https', 'http', 'ftp']
# seed_domain = domain.netloc
seed_domain= tldextract.extract(seed).domain

focused = 'research'

urls = Queue()
urls.put(seed)
visited = []
skipped = []

# Handle robots.txt
rp = robotparser.RobotFileParser()
rp.set_url(seed + "/robots.txt")
rp.read()
myfile = open('crawled_url', 'a')
myfile2 = open('queue', 'a')
myfile4 = open('before_after', 'a')
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
		visited.append(str(url))
		myfile.write(str(url)+"\n")

		soup = BeautifulSoup(page_source, from_encoding='utf-8')

		for link in soup.find_all('a'):
			new_link = link.get('href')
			if new_link is None:
				continue
			#normalize new_link
			myfile4.write("before: " + new_link + "\n")
			new_link = normalize_url(url, new_link)
			myfile4.write("after: " + new_link + "\n")
			if not new_link:
				continue
			# limit page crawling within a given Web domain
			# new_link_domain = urlparse(new_link).netloc
			new_link_domain = tldextract.extract(new_link).domain
			if (new_link_domain == seed_domain
				and	new_link not in visited):
				if len(focused) > 0: # for basic focused crawling
					if focused in new_link:
						urls.put(new_link)
						myfile2.write(new_link+"\n")
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

myfile.close()
myfile2.close()
myfile4.close()