import json
import datetime
import urllib.request as ul
from os.path import exists
import re
from bs4 import BeautifulSoup as soup

baseUrl = "https://dlrg.de/mitmachen/"
# standorteUrl = baseUrl + "/ueber-uns/standorte/"
date = datetime.date.today().strftime("%Y%m%d")


def getPage(url):
    req = ul.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'})
    client = ul.urlopen(req)
    htmldata = client.read()
    client.close()

    return soup(htmldata, "html.parser")


def saveResult(filename, result):
    f = open(filename, "w", encoding="utf-8")
    f.write(json.dumps(result, indent=4))
    f.close()


def getPQLinks():
    filename = "{}-{}.txt".format(date, "links")

    if exists(filename):
        return json.load(open(filename))

    quizzes = {}
    html = getPage(baseUrl)
    anchors = html.find_all("a", href=re.compile("/.*pruefungsfragenquiz.*"))

    for a in anchors:
        url = a.attrs["href"]
        name = a.attrs["title"]
        quizzes[name] = url

    saveResult(filename, quizzes)

    return quizzes


def getLinkWithToken():
    filename = "{}-{}.txt".format(date, "LinksWithToken")

    # if exists(filename):
    #     return json.load(open(filename))

    pagelinks = getPQLinks()
    links = {}

    for name, url in pagelinks.items():
        html = getPage(baseUrl[:-10] + url)
        scripts = html.find_all("script")

        for script in scripts:
            # https://services.dlrg.net/service.php?doc=quiz&strict=1&token=f01aeb78401c129acfc9c6a57828f9a0
            start = script.text.find("https://services.dlrg.net/service.php?doc=quiz&strict=1&token=")
            
            if start != -1:
                links[name] = script.text[start : start + 62 + 32]

    saveResult(filename, links)

    return links


if __name__ == "__main__":
    getPQLinks()
    getLinkWithToken()
