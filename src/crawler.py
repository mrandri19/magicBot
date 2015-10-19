from flask import Flask, render_template, request
from pyquery import PyQuery as pq
import pyjade
import requests
import json

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def index():
    TEMPLATE_NAME = 'index.jade'
    cards = []
    if request.method == 'GET':
        data = None
        return render_template(TEMPLATE_NAME, results = data)
    if request.method == 'POST':
        card_names = parse_request(request.form['cards'])
        for card_name in card_names:
            tmp_card = {}
            card_hrefs = search_card(card_name)
            card_prices = get_card_prices(card_hrefs)

            tmp_card["name"] = card_name
            tmp_card["prices"] = card_prices
            cards.append(tmp_card)

        return_str =""
        for card in cards:
            return_str = return_str + json.dumps(card) + ","
        return render_template(TEMPLATE_NAME, results=return_str)


def parse_request(cards_requested):
    cards_requested = cards_requested.lower().splitlines()
    return cards_requested

def search_card(card_name):
    # Download the search page
    payload = {"mainPage": "showSearchResult", "searchFor": card_name}
    URL = "https://it.magiccardmarket.eu/"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.10 Safari/537.36'}
    r = requests.get(URL , params=payload, headers=HEADERS)

    card_hrefs = parse_search_page(r.text, card_name)
    return card_hrefs

def parse_search_page(body, card_name):
    parsed_card_hrefs = []

    d = pq(body, parser='html')
    card_hrefs = d("tbody > tr > td.col_3 > a").items()

    for href in card_hrefs:
        if href.text().lower() == card_name:
            parsed_card_hrefs.append(href.attr("href"))

    return parsed_card_hrefs

def get_card_prices(card_hrefs):
    card_prices = []
    for card_href in card_hrefs:
        card_url = "https://it.magiccardmarket.eu"
        card_url += card_href

        r = requests.get(card_url)
        card_prices.append(parse_price_page(r.text))

    return card_prices

def parse_price_page(body):
    d = pq(body, parser='html')
    card_price = d("#Dettagliprodotto > div > div.prodDetails > div:nth-child(3) > table > tbody > tr.row_Even.row_2 > td.outerRight.col_Odd.col_1.cell_2_1").text()
    if card_price is not None:
        return card_price
    return False

if __name__ == '__main__':
    app.run()
