from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json, smtplib, ssl, yaml
import emailconfig as cfg

port = 587
smtp_server = "smtp.gmail.com"
sender_email = cfg.sender_email["email"]
sender_password = cfg.sender_email["password"]
receiver_emails = cfg.receiver_emails["emails"].split(", ")

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
        cardDataDict = {"data":[]}
        #I'm adding this as a dictionary for proper data structure
        for i in range(len(allSearchResultSpansNames)):
            card = {}
            card["name"] = allSearchResultSpansNames[i].contents
            card["price"] = allSearchResultSpansPrice[i].contents
            cardDataDict["data"].append(card)
            print("Adding " + json.dumps(card) + " to card data")
        cardDataStr = json.dumps(cardDataDict)
        cardDataJson = json.loads(cardDataStr)
        cardDataYaml = yaml.dump(cardDataJson)
        cardDataYamlStr = str(cardDataYaml)
        print(cardDataYamlStr)
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            for email in receiver_emails:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = email
                msg['Subject'] = "Dogmatika update " + str(datetime.now())
                msg.attach(MIMEText(cardDataYamlStr, 'plain'))
                print("Sending email to " + email)
                server.sendmail(sender_email, email, msg.as_string())
if __name__=="__main__":
    main()
