# import library
from bs4 import BeautifulSoup
import requests
import colorama
from pprint import pprint
import csv

# Set up the list of color using for printing
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE

# Request to website and download HTML contents
url = "https://www.philadelphiafed.org/"
req = requests.get(url)
content = req.text

my_data = []

# Create a file to write to, add headers row
outputFile = csv.writer(open('articles.csv', 'w'))
outputFile.writerow(['Date', 'Excerpt'])

# Create a Beautiful Soup object
soup = BeautifulSoup(content, "html.parser")

articles = soup.select('div.card-body')
print(f"{GREEN}Total found articles: {len(articles)}\n{RESET}")

for article in articles:
    articleDate = article.select('p.article-date')[0].get_text()
    articleExcerpt = article.select('p.article-excerpt')[0].get_text()

    my_data.append({"Date": articleDate, "Excerpt": articleExcerpt})

    print(f"{BLUE}{articleDate}{RESET}")
    print(f"{articleExcerpt}\n")

    # Add each article to a row of the output csv file
    outputFile.writerow([articleDate, articleExcerpt])

print(f"{BLUE}------- Printing data as JSON format ------- {RESET}")
pprint(my_data)