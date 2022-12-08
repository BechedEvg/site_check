from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
import os
import re
import json


class DriverChrome:

    def __init__(self):
        self.driver = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument("start-maximized")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

    def open_browser(self):
        self.driver = webdriver.Chrome(options=self.options, service=Service(rf"{os.getcwd()}/chromedriver"))

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def close_browser(self):
        self.driver.quit()


def json_write(result_dict):
    with open('Result.json', 'w', encoding="utf-8") as outfile:
        json.dump(result_dict, outfile, indent=4, ensure_ascii=False)


# add mobile page title length to page dictionary from (desktop check)
def add_mobile_title_len(domain, desktop_dict):
    url = f"https://www.google.com/search?q=site:{domain}&num=100&start=0"
    page_list = get_site_page(url, device="mobile")
    start = 100
    while True:
        for page in page_list:
            page_url = page.find(class_="P8ujBc jqWpsc").find("a")["href"]
            title = page.find(class_="oewGkc LeUQr MUxGbd v0nnCb").text
            if page_url in desktop_dict["dict_page"]:
                desktop_dict["dict_page"][page_url]["len_title_mobile"] = len(title)
        url = f"https://www.google.com/search?q=site:{domain}&num=100&start={start}"
        page_list = get_site_page(url, device="mobile")
        if len(page_list) != 0:
            start += 100
        else:
            break
    return desktop_dict


# get a dictionary of all pages with data from the check in the search engine
# (desktop check)
def get_desktop_dict_page(domain):
    url = f"https://www.google.com/search?q=site:{domain}&num=100&start=0"
    number_pages = check_number_pages(url)
    page_list, url = get_site_page(url)
    dict_domain = {"number_pages": number_pages, "dict_page": {}}
    while True:
        for page in page_list:
            page_url = page.find(class_="yuRUbf").find("a")["href"]
            description = page.find(class_=re.compile("VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc")).text.replace(u'\xa0', u' ')
            title = page.find(class_="LC20lb MBeuO DKV0Md").text
            dict_domain["dict_page"][page_url] = {
                "title": title,
                "description": description,
                "len_title_desktop": len(title)
            }
        if url:
            page_list, url = get_site_page(url)
        else:
            break
    return dict_domain


# get number of pages in search
def check_number_pages(url):
    html_search = get_html(url)
    parser = BeautifulSoup(html_search, "lxml")
    number_pages = (parser.find(class_="LHJvCe").text.split()[2:-2])
    return "".join(number_pages)


# check if the next page is in the search query and return its link
def check_next_page(html_search):
    parser = BeautifulSoup(html_search, "lxml")
    try:
        next_page = "https://www.google.com"
        next_page += parser.find(jsname="TeSSVd").find_all(class_="d6cvqb BBwThe")[-1].find("a")["href"]
        return next_page
    except:
        return False


# get page html
def get_html(url):
    browser = DriverChrome()
    browser.open_browser()
    browser.driver.get(url)
    html = browser.driver.find_element(By.XPATH, "/html")
    html = html.get_attribute("innerHTML")
    browser.close_browser()
    return html


# get page html from mobile emulation
def get_mobile_html(url):
    browser = DriverChrome()
    browser.options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, likeGecko) Version/10.0 Mobile/14E304 Safari/602.1")
    mobileEmulation = {'deviceName': 'iPhone 8'}
    browser.options.add_experimental_option('mobileEmulation', mobileEmulation)
    browser.open_browser()
    browser.driver.get(url)
    html = browser.driver.find_element(By.XPATH, "/html")
    html = html.get_attribute("innerHTML")
    browser.close_browser()
    return html


# Get a list of classes with page data depending on the device.
# (returns a link to go to the next search page if devise=desktop)
def get_site_page(url, device="desktop"):
    if device == "desktop":
        html_search = get_html(url)
        next_page = check_next_page(html_search)
        parser = BeautifulSoup(html_search, "lxml")
        page_list = parser.find_all(class_="MjjYud")
        return page_list, next_page
    elif device == "mobile":
        html_search = get_mobile_html(url)
        parser = BeautifulSoup(html_search, "lxml")
        page_list = parser.find_all(class_="MjjYud")
        return page_list


def main():
    domain = input()
    desktop_dict_page = get_desktop_dict_page(domain)
    result_dict = add_mobile_title_len(domain, desktop_dict_page)
    json_write(result_dict)


if __name__ == "__main__":
    main()
