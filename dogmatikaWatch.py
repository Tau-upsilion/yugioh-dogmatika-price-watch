from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import json

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error("Error during request to {0} : {1}".format(url, str(e)))
        return None
def is_good_response(resp):
    content_type = resp.headers["Content-Type"].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
def log_error(e):
    print(e)

def main():
    response = simple_get("https://www.tcgplayer.com/search/all/product?q=dogmatika")
    print("Running the simple get method")
    if response is not None:
        session = HTMLSession()
        resp = session.get("https://www.tcgplayer.com/search/all/product?q=dogmatika")
        resp.html.render()
        html = BeautifulSoup(resp.html.html, "html.parser")
        allSearchResultSpansNames = html.findAll("span", {"class": "search-result__title"})
        allSearchResultSpansPrice = html.findAll("span", {"class": "inventory__price-with-shipping"})
        cardData = {"data":[]}
        for i in range(len(allSearchResultSpansNames)):
            card = {}
            card["name"] = allSearchResultSpansNames[i].contents
            card["price"] = allSearchResultSpansPrice[i].contents
            cardData["data"].append(card)
            print("I just added " + card)
        print(cardData)
if __name__=="__main__":
    main()
