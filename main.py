from bs4 import BeautifulSoup
import json
import cloudscraper
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from time import sleep
from usp.tree  import sitemap_tree_for_homepage


class DriverChrome:

    def __init__(self):
        self.driver = None
        self.options = webdriver.ChromeOptions()
        #self.options.add_argument('headless')
        self.options.add_argument("start-maximized")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

    def open_browser(self):
        self.driver = webdriver.Chrome(options=self.options, service=Service(rf"{os.getcwd()}/chromedriver"))

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win64",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def close_browser(self):
        self.driver.quit()


# getting main tags from HEAD
class ScrapingHead:

    def __init__(self, source_page):
        self.parser = BeautifulSoup(source_page, 'lxml')

    def get_title(self):
        try:
            title = self.parser.find("head").find("title").text
            return title
        except:
            return "not_found"

    def get_description(self):
        try:
            description = self.parser.find("head").find(attrs={"name": "description"}).get("content")
            return description
        except:
            pass
        try:
            description = self.parser.find("head").find(attrs={"property": "og:description"}).get("content")
            return description
        except:
            return "not_found"

    def get_tag_canonical(self):
        try:
            title = self.parser.find("head").find("link", {"rel": "canonical"}).get("href")
            return title
        except:
            return "not_found"


class JsonRW:

    def json_write(self, name, in_dict):
        with open(f'{name}.json', 'w') as outfile:
            json.dump(in_dict, outfile, indent=4, ensure_ascii=False)

    def json_read(self, name):
        with open(f'{name}.json', 'r') as infile:
            return json.load(infile)


def check_robots(url):
    robot_check = {"user_agent": [], "url_sitemap": "not_found"}
    patch_robot = url + "/robots.txt"
    user_agent_list = []
    page_robot = get_url(patch_robot)
    if page_robot.status_code == 200:
        try:
            page_robot.text.split("Sitemap:")[1].split()[0]
            robot_check["url_sitemap"] = "found"
        except:
            pass
        try:
            robots_line = page_robot.text.split("\n")

            for line, par in zip(robots_line[::2], robots_line[1::2]):
                line_list = line.split()

                if line_list[0].lower() == "user-agent:":
                    user_agent = line_list[1]
                    rule = par.split()

                    if rule[0].lower() == "disallow:":
                        if len(rule) == 1 or rule[1] != "/":
                            user_agent_list.append(user_agent)
        except:
            pass

    if "*" in user_agent_list:
        robot_check["user_agent"].append("*")
    else:
        robot_check["user_agent"] += user_agent_list
    return robot_check


# check for google code on page
def check_cod_google(source_page):
    parser = BeautifulSoup(source_page, 'lxml')
    dict_google_cod = {"analytics(ua)": "not_found", "analytics(ga4)": "not_found"}
    script = str(parser.find_all('script', {"src": True}))
    if script.find("googletagmanager.com/gtag/js") != -1:
        dict_google_cod["analytics(ga4)"] = "found"

    if script.find("google-analytics.com/analytics.js") != -1:
        dict_google_cod["analytics(ua)"] = "found"
    return dict_google_cod


# get list of img tags
def check_alt_img(source_page):
    parser = BeautifulSoup(source_page, 'lxml')
    img = parser.find_all("img")
    dit_img = {"img_amount": 0, "list_atl": []}
    for i in img:
        dit_img["img_amount"] += 1
        try:
            dit_img["list_atl"].append(i["alt"])
        except:
            pass
    return dit_img


# get structure and content of H tags
def get_teg_h(source_page):
    parser = BeautifulSoup(source_page, 'lxml')
    list_tag_h = parser.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    dict_tag = {"h1": {"count": 0, "list_source": []}, "list_tag": []}
    for tag in list_tag_h:
        h = str(tag).split()[0][1:3]

        if h == "h1":
            dict_tag["h1"]["count"] += 1
            dict_tag["h1"]["list_source"].append(str(tag))

        if h not in dict_tag["list_tag"]:
            dict_tag["list_tag"].append(h)

    if len(dict_tag["list_tag"]) != 0:
        return dict_tag
    else:
        return "not_found"


# checking if two links belong to the same domain
def check_domain(url_page, link):
    try:
        url_page = url_page.split('/')[2]
        link = link.split('/')[2]
        if url_page.split(".")[0].lower() == "www":
            url_page = link[4:]

        if link.split(".")[0].lower() == "www":
            link = link[4:]

        if link == url_page:
            return True

        return False
    except:
        return False


# get list of external links
def get_external_link(url, source_page):
    parser = BeautifulSoup(source_page, 'lxml')
    parser.find_all("a")
    list_link = []
    for page_element in parser.find_all("a"):
        try:
            link = page_element["href"]
            if link.split("/")[0] == "https:" or link.split("/")[0] == "http:":
                if not check_domain(url, link):
                    list_link.append(link)
        except:
            pass
    return list_link


# get page code with webdriver
def get_page_source_webdriver(url):
    browser = DriverChrome()
    browser.open_browser()
    browser.driver.get(url)
    html = browser.driver.page_source
    browser.close_browser()
    return html



def get_url(url):
    scraper = cloudscraper.create_scraper()
    try:
        return scraper.get(url)
    except:
        return "no_connection"


# get all pages of a site from a sitemap
def get_url_list_in_sitemap(sitemap):
    list_page = []
    for page in sitemap_tree_for_homepage(sitemap).all_pages():
        if page.url not in list_page:
            list_page.append(page.url)
    return list_page


# check for a sitemap and get a link to it
def check_sitemap(url):
    sitemap = url + "/sitemap.xml"
    if get_url(sitemap).status_code == 200:
        return sitemap

    sitemap = url + "/robots.txt"
    if get_url(sitemap).status_code == 200:
        try:
            sitemap = get_url(sitemap).text.split("Sitemap:")[1].split()[0]
            return sitemap
        except:
            pass

    return "not_found"


# obtaining a ready-made dictionary with data for all pages
def get_result_dict(sitemap, url):
    robots = check_robots(url)
    result_dict = {"robots": robots, "sitemap": sitemap, "page_list": {}}
    page_site_google_result = [page for page in JsonRW().json_read("google_result")]

    if sitemap != "not_found":
        page_site_sitemap = get_url_list_in_sitemap(sitemap)
        page_site = list(filter(lambda x: True if x not in  page_site_google_result else False, page_site_sitemap))
        page_site += page_site_google_result
    else:
        page_site = page_site_google_result

    for page in page_site:
        status_code = get_url(page)

        if status_code != "no_connection":
            status_code = status_code.status_code
            result_dict["page_list"][page] = {"status_code": status_code}

            if status_code == 200:
                page_source = get_page_source_webdriver(page)
                scraper_head = ScrapingHead(page_source)
                result_dict["page_list"][page]["page_content"] = {
                    "title": scraper_head.get_title(),
                    "description": scraper_head.get_description(),
                    "canonical": scraper_head.get_tag_canonical(),
                    "list_tag": get_teg_h(page_source),
                    "images_alt": check_alt_img(page_source),
                    "external_link": get_external_link(page, page_source),
                    "google_cod": check_cod_google(page_source),
                }
    return result_dict


# site check main function
def check_site(url):
    base_status_code = get_url(url)
    if base_status_code != "no_connection":
        base_status_code = base_status_code.status_code
        sitemap = check_sitemap(url)

        if base_status_code == 200:
            result_dict = get_result_dict(sitemap, url)
            return result_dict

        elif base_status_code != 200:
            return f"we can't scan this resource because it responds with a {base_status_code} HTTP status code."

    return "no_connection"


def main():
    site = input()
    JsonRW().json_write("check_result", check_site(site))


if __name__ == "__main__":
    main()
