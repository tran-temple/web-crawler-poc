import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio
import random
import colorama
import socket
import sys
from fake_useragent import UserAgent

class HostHeaderSSLAdapter(requests.adapters.HTTPAdapter):

    ipDict = {}

    def resolve(self, hostname):
        # a dummy DNS resolver
        import random
        ip = ''
        if hostname in self.ipDict.keys():
            print('reuse')
            ip = self.ipDict[hostname]
        else:
            print('add new')
            ip = socket.gethostbyname(hostname)
            self.ipDict[hostname] = ip
        print(self.ipDict)
        print('resolve: ', ip)
        return ip

    def send(self, request, **kwargs):
        from urllib.parse import urlparse

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        result = urlparse(request.url)
        resolved_ip = self.resolve(result.hostname)

        if result.scheme == 'https' and resolved_ip:
            request.url = request.url.replace(
                'https://' + result.hostname,
                'https://' + resolved_ip,
            )
            connection_pool_kwargs['server_hostname'] = result.hostname  # SNI
            connection_pool_kwargs['assert_hostname'] = result.hostname

            # overwrite the host header
            request.headers['Host'] = result.hostname
        else:
            # theses headers from a previous request may have been left
            connection_pool_kwargs.pop('server_hostname', None)
            connection_pool_kwargs.pop('assert_hostname', None)

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)


    

seenLinks = {}

rootNode = {}
currentNode = {}

linksQueue = []
printList = []

anchorLinks = []
specialLinks = []
externalLinks = []

previousDepth = 0
maxCrawlingDepth = 5
totalLinks = 0
totalCrawledLinks = 0

mainDomain = None
mainParsedUrl = None
statedTime = None

mainSession = None



# Set up the list of color using for printing
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE

# Constructor to create a specific link object
class CreateLink:
    def __init__(self, linkURL, depth, parent):
        self.url = linkURL
        self.depth = depth
        self.parent = parent
        self.children = []

# This function is to start crawling from the seed page rely on the crawled depth level
async def crawlAll(startURL, maxDepth = 5):
    global rootNode, currentNode, mainDomain, maxCrawlingDepth, mainParsedUrl, startedTime, mainSession
    mainSession = requests.Session()
    retry = Retry(connect=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])

    mainSession.mount("http://", HostHeaderSSLAdapter())
    mainSession.mount("https://", HostHeaderSSLAdapter())


    startedTime = time.time()
    try:
        mainParsedUrl = urlparse(startURL)
        # print("mainParsedURL", mainParsedUrl)
    except ValueError as err:
        print(f"{RED}URL is not valid - {err}{RESET}")
        return
    
    #mainDomain = mainParsedUrl.hostname
    maxCrawlingDepth = maxDepth
    startLinkObj = CreateLink(startURL, 0, None)
    rootNode = currentNode = startLinkObj
    # add to link queue
    addToLinkQueue(startLinkObj)

    # addToLinkQueue(currentNode)
    # await findLinks(currentNode)
    await crawls()
    


    printFurtherInfo()
    print("Run time: ", time.time() - startedTime)


async def crawls():
    #global currentNode, rootNode, maxCrawlingDepth, totalLinks
    global maxCrawlingDepth, totalLinks, totalCrawledLinks, startedTime

    linkObj = getNextInQueue()
    while linkObj is not None and linkObj.depth <= maxCrawlingDepth:
        print(f"{BLUE}Crawling URL: {linkObj.url}{RESET}")
        try:
            ua = UserAgent()
            user_agent = ua.random
            print('user_agent: ', user_agent)
            
            headers = {
                        'User-Agent': user_agent
                    } 
            response = mainSession.get(linkObj.url, headers=headers, timeout=5)
            totalCrawledLinks = totalCrawledLinks + 1

            # Check the status code of page
            if response.status_code >= 200 and response.status_code < 300:
                print(f"{GREEN}--- Status: {response.status_code} - Success, Link is Okay.{RESET}")
            else:
                if response.status_code >= 400 and response.status_code < 500:
                    print(f"{RED}--- Status: {response.status_code} - Client Error, Link is broken! - {RESET}")

                if response.status_code >= 500 and response.status_code < 600:
                    print(f"{RED}--- Status: {response.status_code} - Server Error, Link is broken! - {RESET}")

                if response.status_code >= 600:
                    print(f"{RED}--- Status: {response.status_code} - Link maybe not permited for scanning by host! - {RESET}")

            # Notes for content-type is not html: some links might be the video/mp4, audio/mp3, application/pdf, image, etc. - no need to crawl it or parse it to get text
            contentType = response.headers.get('content-type')

            if "text/html" in contentType :
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all("a", href=True)
                
                if len(links) > 0:
                    print(f"{BLUE}Total links of this URL: {len(links)}{RESET}")
                    totalLinks = totalLinks + len(links)

                    for link in links:
                        # Test ouput link
                        # print("Test output link: " + link["href"])

                        reqLink = checkDomain(link["href"])
                        # print('Test checkDomain: ', reqLink)
                        
                        if reqLink:
                            if reqLink != linkObj.url:
                                # print("pass 1")
                                newLinkObj = CreateLink(reqLink, linkObj.depth + 1, linkObj)
                                # print("pass 2")
                                addToLinkQueue(newLinkObj)
                                # print("pass 3")
                else:
                    print(f"{GRAY}No more links found for {linkObj.url}{RESET}")
            else:
                print(f"{GRAY}No more sub-links found for {linkObj.url}{RESET}")
        except requests.exceptions.ConnectionError as conErr:
            print(f"{RED}ConnectionError {conErr}{RESET}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.Timeout as timeErr: 
            print(f"{RED}Timeout {timeErr}{RESET}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.TooManyRedirects as tooErr:
            print(f"{RED}TooManyRedirects {tooErr}{RESET}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.RequestException as reqErr:
            print(f"{RED}RequestException {reqErr}{RESET}")
            print("Run time: ", time.time() - startedTime)
        except Exception as err:
            print(f"{RED}Something went wrong... {err}{RESET}")
            # await asyncio.sleep(20)
            print("Run time: ", time.time() - startedTime)
            raise SystemExit(err)
            # setRootNode()
            # printTree()

        linkObj = getNextInQueue()
        # print("Test depth - ", nextLinkObj.depth)
        # print("Test maxCrawlingDepth - ", maxCrawlingDepth)
        if linkObj is not None and linkObj.depth > maxCrawlingDepth:
            linkObj = None

    setRootNode()
    printTree()

# This function is to start the function find links of the crawled URL
async def crawl(linkObj):
    await findLinks(linkObj)

# This function is to get the HTML and look for the links inside the page
async def findLinks(linkObj):
    #global currentNode, rootNode, maxCrawlingDepth, totalLinks
    global maxCrawlingDepth, totalLinks, totalCrawledLinks, startedTime

    print(f"{BLUE}Crawling URL: {linkObj.url}{RESET}")

    try:
        # user_agents = [ 
        #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
        #     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
        #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
        #     'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
        #     'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
        # ] 

        # user_agent = random.choice(user_agents) 

        ua = UserAgent()
        user_agent = ua.random
        print('user_agent: ', user_agent)
        
        headers = {
                    'User-Agent': user_agent
                } 
    
        # session = requests.Session()
        # retry = Retry(connect=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
       

        
        # session.mount("http://", HTTPAdapter(max_retries=retry))
        # session.mount("https://", HTTPAdapter(max_retries=retry))
        

        # session.mount("http://", HostHeaderSSLAdapter())
        # session.mount("https://", HostHeaderSSLAdapter())
        #response = requests.get(linkObj.url, timeout=5, headers=headers)

        response = mainSession.get(linkObj.url, headers=headers, timeout=5)
        totalCrawledLinks = totalCrawledLinks + 1

        # Check the status code of page
        if response.status_code >= 200 and response.status_code < 300:
            print(f"{GREEN}--- Status: {response.status_code} - Success, Link is Okay.{RESET}")
        else:
            if response.status_code >= 400 and response.status_code < 500:
                print(f"{RED}--- Status: {response.status_code} - Client Error, Link is broken! - {RESET}")

            if response.status_code >= 500 and response.status_code < 600:
                print(f"{RED}--- Status: {response.status_code} - Server Error, Link is broken! - {RESET}")

            if response.status_code >= 600:
                print(f"{RED}--- Status: {response.status_code} - Link maybe not permited for scanning by host! - {RESET}")

        # Notes for content-type is not html: some links might be the video/mp4, audio/mp3, application/pdf, image, etc. - no need to crawl it or parse it to get text
        contentType = response.headers.get('content-type')

        if "text/html" in contentType :
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            if len(links) > 0:
                print(f"{BLUE}Total links of this URL: {len(links)}{RESET}")
                totalLinks = totalLinks + len(links)

                for link in links:
                    # Test ouput link
                    # print("Test output link: " + link["href"])

                    reqLink = checkDomain(link["href"])
                    # print('Test checkDomain: ', reqLink)
                    
                    if reqLink:
                        if reqLink != linkObj.url:
                            # print("pass 1")
                            newLinkObj = CreateLink(reqLink, linkObj.depth + 1, linkObj)
                            # print("pass 2")
                            addToLinkQueue(newLinkObj)
                            # print("pass 3")
            else:
                print(f"{GRAY}No more links found for {linkObj.url}{RESET}")
        else:
            print(f"{GRAY}No more sub-links found for {linkObj.url}{RESET}")
    except requests.exceptions.ConnectionError as conErr:
        print(f"{RED}ConnectionError {conErr}{RESET}")
        print("Run time: ", time.time() - startedTime)
    except requests.exceptions.Timeout as timeErr: 
        print(f"{RED}Timeout {timeErr}{RESET}")
        print("Run time: ", time.time() - startedTime)
    except requests.exceptions.TooManyRedirects as tooErr:
        print(f"{RED}TooManyRedirects {tooErr}{RESET}")
        print("Run time: ", time.time() - startedTime)
    except requests.exceptions.RequestException as reqErr:
        print(f"{RED}RequestException {reqErr}{RESET}")
        print("Run time: ", time.time() - startedTime)
    except Exception as err:
        print(f"{RED}Something went wrong... {err}{RESET}")
        # await asyncio.sleep(20)
        print("Run time: ", time.time() - startedTime)
        raise SystemExit(err)
        # setRootNode()
        # printTree()

    nextLinkObj = getNextInQueue()
    # print("Test depth - ", nextLinkObj.depth)
    # print("Test maxCrawlingDepth - ", maxCrawlingDepth)
    if nextLinkObj and nextLinkObj.depth <= maxCrawlingDepth:
        #Random sleep
        #It is very important to make this long enough to avoid spamming the website we want to scrape
        #if we choose a short time we will potentially be blocked or kill the website we want to crawl
        #time is in seconds here
        # miniumWaitTime = 0.5
        # maxiumWaitTime = 5
        # waitTime = round(miniumWaitTime + (random.random() * (maxiumWaitTime - miniumWaitTime)))
        # print(f"{GRAY}Wait for {waitTime} seconds{RESET}")
        # time.sleep(waitTime)
        # waitTime = 1
        # await asyncio.sleep(waitTime)
        # next url crawling
        await crawl(nextLinkObj)
    else:
        setRootNode()
        printTree()

# This function is to check domain of the crawled URL
def checkDomain(linkURL):
    global mainParsedUrl, mainDomain, currentNode, externalLinks, anchorLinks, specialLinks
    
    try:
        parsedUrl = urlparse(linkURL)
        
        if parsedUrl.hostname is None:
            if linkURL.startswith("/"):
                # relative to domain url
                # print("Relative to domain url - " + mainParsedUrl.scheme + "://" + mainParsedUrl.netloc + linkURL.split("#")[0])
                return mainParsedUrl.scheme + "://" + mainParsedUrl.netloc + linkURL.strip().split("#")[0]
            elif linkURL.startswith("#"):
                # anchor, avoid link
                # print("Avoid link: Yes - return None: no crawling it")
                if not linkURL in anchorLinks:
                    anchorLinks.append(linkURL)
                return None
            elif linkURL.startswith("mailto:") or linkURL.startswith("tel:"):
                if not linkURL in specialLinks:
                    specialLinks.append(linkURL)
                return None
            else:
                # relative url
                path = "/".join(currentNode.url.split("/")[:-1]) + "/"
                # print("Path - " + path)
                # print("Relative url - " + urljoin(path, linkURL))
                return urljoin(path, linkURL)
        
        mainHostDomain = parsedUrl.hostname
        
        if mainDomain == mainHostDomain:
            # print("Absoluate internal link: " + linkURL)
            return linkURL
        else:
            # print("External link: Yes - return None: no crawling it")
            if not linkURL in externalLinks:
                externalLinks.append(linkURL)
            return None
    except Exception as err:
        print(f"{RED}Exception Error during checking domain: {err}{RESET}")
        return None

# This function is to set the root page
def setRootNode():
    global currentNode, rootNode
    while currentNode.parent is not None:
        currentNode = currentNode.parent
    rootNode = currentNode

# This function is to print all internal links like a tree
def printTree():
    global rootNode, printList
    addToPrint(rootNode)
    print("\n|".join(printList))
    totalITLinks = len(printList)
    print(f"{GREEN}Total Crawled Internal Links (exclude duplicates): {totalCrawledLinks}{RESET}")
    print(f"{GREEN}Total Internal Links (exclude duplicates): {totalITLinks}{RESET}")

def printFurtherInfo():
    global anchorLinks, specialLinks, externalLinks, totalLinks
    # Print further information
    print("---------- Anchor Links ----------")
    # print("\n".join(anchorLinks))
    print(f"{GREEN}Total Anchor Links: {len(anchorLinks)}{RESET}")

    print("---------- Special Links ----------")
    # print("\n".join(specialLinks))
    print(f"{GREEN}Total Special Links: {len(specialLinks)}{RESET}")

    print("---------- External Links ----------")
    # print("\n".join(externalLinks))
    print(f"{GREEN}Total External Links: {len(externalLinks)}{RESET}")

    # checkExternalLinks()

    print(f"{BLUE}Total links: {totalLinks}{RESET}")

def checkExternalLinks():
    global externalLinks, startedTime
    
    for link in externalLinks:
        try:
            ua = UserAgent()
            user_agent = ua.random
            print('user_agent: ', user_agent)
            
            headers = {
                        'User-Agent': user_agent
                    } 
            response = mainSession.get(link, headers=headers, timeout=5)
            # response = requests.get(link, timeout = 30)
            print(f"- Checking external link: {link}")
            # Check the status code of page
            if response.status_code >= 200 and response.status_code < 300:
                print(f"{GREEN}--- Status: {response.status_code} - Success, Link is Okay.{RESET}")
            else:
                if response.status_code >= 400 and response.status_code < 500:
                    print(f"{RED}--- Status: {response.status_code} - Client Error, Link is broken! - {RESET}")

                if response.status_code >= 500 and response.status_code < 600:
                    print(f"{RED}--- Status: {response.status_code} - Server Error, Link is broken! - {RESET}")

                if response.status_code >= 600:
                    print(f"{RED}--- Status: {response.status_code} - Link maybe not permited for scanning by host! - {RESET}")
        except requests.exceptions.ConnectionError as conErr:
            print(f"{RED}ConnectionError {conErr}{RESET}")
            print(f"-External link: {link}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.Timeout as timeErr: 
            print(f"{RED}Timeout {timeErr}{RESET}")
            print(f"-External link: {link}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.TooManyRedirects as tooErr:
            print(f"{RED}TooManyRedirects {tooErr}{RESET}")
            print(f"-External link: {link}")
            print("Run time: ", time.time() - startedTime)
        except requests.exceptions.RequestException as reqErr:
            print(f"{RED}RequestException {reqErr}{RESET}")
            print(f"-External link: {link}")
            print("Run time: ", time.time() - startedTime)
        except Exception as err:
            print(f"{RED}Something went wrong... {err}{RESET}")
            print(f"-External link: {link}")
            # await asyncio.sleep(20)
            print("Run time: ", time.time() - startedTime)
            raise SystemExit(err)
    

# This function is to add links for printing
def addToPrint(node):
    global printList
    spaces = "-" * (node.depth * 3)
    printList.append(spaces + node.url)
    if node.children:
        for child in node.children:
            addToPrint(child)

# This function is to add the link to the queue if it is not seen and crawled
def addToLinkQueue(linkObj):
    global linksQueue
    if not linkInSeenListExists(linkObj):
        if linkObj.parent is not None:
            linkObj.parent.children.append(linkObj)
        linksQueue.append(linkObj)
        addToSeen(linkObj)

# This function is to get the link for crawling
def getNextInQueue():
    global linksQueue, previousDepth
    if len(linksQueue) > 0:
        nextLink = linksQueue.pop(0)
        if nextLink and nextLink.depth > previousDepth:
            previousDepth = nextLink.depth
            print(f"------- Crawling on Depth Level {previousDepth} --------")
        return nextLink
    return None

# This function is to add to the list of seen links
def addToSeen(linkObj):
    global seenLinks
    seenLinks[linkObj.url] = linkObj

# This function is to check the link is already in the seen links list
def linkInSeenListExists(linkObj):
    global seenLinks
    return linkObj.url in seenLinks

# This is the main function to execute, 
if __name__ == "__main__":
    # sys.setrecursionlimit(10000)
    # rootURL = "https://www.consumercomplianceoutlook.org/"
    rootURL = "https://www.philadelphiafed.org/"
    depth = 10
    # Test crawling
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawlAll(rootURL, depth))
    loop.close()
