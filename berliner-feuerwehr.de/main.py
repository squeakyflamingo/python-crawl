import json
import datetime
import urllib.request as ul
from os.path import exists
import re
from bs4 import BeautifulSoup as soup

baseUrl = "https://www.berliner-feuerwehr.de"
standorteUrl = baseUrl + "/ueber-uns/standorte/"
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


def getWachen():
    filename = "{}-{}.txt".format(date, "Wachen")

    if exists(filename):
        return json.load(open(filename))

    wachen = {}
    html = getPage(standorteUrl)
    anchors = html.find_all("a", href=re.compile("/ueber-uns/standorte/[\w-]*/"))

    for a in anchors:
        url = a.attrs["href"]
        name = a.strong.contents[0]
        wache = name[-4:]
        wachen[wache] = {"name": name, "url": url}

    saveResult(filename, wachen)

    return wachen


def getFahrzeuge():
    filename = "{}-{}.txt".format(date, "Fahrzeuge")

    if exists(filename):
        return json.load(open(filename))

    wachen = getWachen()
    alleFahrzeuge = {}

    for wache, value in wachen.items():
        print(value["name"])
        html = getPage(baseUrl + value["url"])
        fzbf = html.find_all("div", class_="fzbf")

        fahrzeugListe = []

        for div in fzbf:
            for caption in div.find_all("figcaption"):
                fahrzeug = caption.contents[0]
                if re.match("^(?!.*(Besatzung|0{3})).*(\d{4})$", fahrzeug):  # Filtern von Stützpunktfahrzeugen
                    continue
                fahrzeugListe.append(fahrzeug)

        alleFahrzeuge[wache] = fahrzeugListe

    saveResult(filename, alleFahrzeuge)

    return alleFahrzeuge


def getRTW():
    filename = "{}-{}.txt".format(date, "RTW")

    if exists(filename):
        return json.load(open(filename))

    alleFahrzeuge = getFahrzeuge()
    gefilterteFahrzeuge = {}

    for wache, fahrzeugListe in alleFahrzeuge.items():
        gefilterteFahrzeuge[wache] = [f for f in fahrzeugListe if re.match(".*RTW.*", f)]
        if not gefilterteFahrzeuge[wache]:
            gefilterteFahrzeuge.popitem()

    saveResult(filename, gefilterteFahrzeuge)


if __name__ == "__main__":
    getWachen()
    getFahrzeuge()
    getRTW()
