## **Building a basic web crawler with Beautiful Soup and Requests**
This repository contains samples to show how to use Python libraries such as Beautiful Soup and Requests to build a basic web crawler.

### **Getting Started**
1. Install Homebrew (it’s a package management system that makes it easier to install software on Mac OS machines)
    
    Please follow the instructions on the website [Homebrew](https://brew.sh/) to install.

    **Note:** Homebrew manages all updating/upgrading by itself.
    - Run brew update && brew upgrade every once in a while (and you can do it after upgrading macOS)
    - Brew update will update the list of available formulae, and brew upgrade will upgrade any outdated packages.
    ```
    brew update && brew upgrade
    ```
2. Install python3 using Homebrew & check the version
    ```
    brew install python3
    python3 --version
    ```
3. Navigate to the project directory and create the virtal environment
    ```
    python3 -m venv <name of virtual enviornment>
    ```
    For example, the name of my virtual environment is venv:
    ```
    python3 -m venv venv
    ```
4. Activate the virtual environment before installing Python dependencies
    ```
    source venv/bin/activate
    ```
5. Install Python dependencies
    ```
    pip install beautifulsoup4
    pip install requests
    pip install colorama
    ```
    **Note:**
    - Beautiful Soup is a Python library for pulling data out of HTML and XML files. It works with your favorite parser to provide idiomatic ways of navigating, searching and modifying the parse tree. It commonly saves programmers hours or days of work.
    - Requests is a favorite library in the Python community because it is concise and easy to use. Requests is powered by urllib3 and jokingly claims to be the “The only Non-GMO HTTP library for Python, safe for human consumption.” Requests abstracts a lot of boilerplate code and makes HTTP requests simpler than using the built-in urllib library.
    - The Colorama is one of the built-in Python modules to display the text in different colors. It is used to make the code more readable.

### **Run sample scripts**
1. The basic_web_crawler.py script will scrape data such as articles of the homepage [philadelphiafed.org](https://www.philadelphiafed.org/) and output to the articles.csv file 
```
python basic_web_crawler.py
```
The Console Log of running basic_web_crawler.py script:
![Console Log of running basic_web_crawler.py script](./images/Basic%20Web%20Crawler.png)


2. The web_crawler_links.py script will scrape all the links found based on the depth that you want to crawl.
    - Put the adress where you want to start your crawling with
    - Put the depth level
        ```
        rootURL = "https://www.consumercomplianceoutlook.org/"
        depth = 1
        ```
        For example:
    
        - Depth 1 - it will scrape all the links found on the first page but not the ones found on other pages
        - Depth 2 - it will scrape all links on first page and all links found on second level pages

        **Notes:** Be careful with this on a huge website it will represent tons of pages to scrape. It is recommended to limit to 5 levels.
```
python web_crawler_links.py
```
The Console Log of running web_crawler_links.py script:
![Console Log 1 of running web_crawler_links.py script](./images/Crawling%20URLs%20level%201-1.png)
![Console Log 2 of running web_crawler_links.py script](./images/Crawling%20URLs%20level%201-2.png)

### **References**
- [Beautiful Soup Documentation](https://beautiful-soup-4.readthedocs.io/en/latest/)
- RealPython - [Python’s Requests Library (Guide)](https://realpython.com/python-requests/)
- [List of HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
- Towards Data Science - [Web Scraping Basics: How to scrape data from a website in Python](https://towardsdatascience.com/web-scraping-basics-82f8b5acd45c)
- PythonCode - [How to Extract All Website Links in Python](https://www.thepythoncode.com/article/extract-all-website-links-python)
- ScrapingBot - [How to build a web crawler?](https://www.scraping-bot.io/how-to-build-a-web-crawler/)
- Hackernoon - [How to Master Web Scraping in Python: From Zero to Hero](https://hackernoon.com/how-to-master-web-scraping-in-python-from-zero-to-hero/)
