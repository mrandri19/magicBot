from flask import Flask, render_template, request
from pyquery import PyQuery as pq
import pyjade
import requests
import json
from statistics import mean
from threading import Thread
from queue import Queue

TEMPLATE_NAME_INDEX = "index.jade"
TEMPLATE_NAME_RESULTS = "results.jade"
TEMPLATE_FOLDER = "../templates/"

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def index():
    cards = []
    if request.method == 'GET':
        data = None
        return render_template(TEMPLATE_NAME_INDEX, results = data)
    if request.method == 'POST':
        card_names = parse_request(request.form['cards'])
        for card_name in card_names:
            tmp_card = {}
            card_hrefs = search_card(card_name)
            card_prices = get_card_prices(card_hrefs)

            tmp_card["prices"] = parse_card_prices(card_prices)
            tmp_card["name"] = card_name

            cards.append(tmp_card)

        return render_template(TEMPLATE_NAME_RESULTS, results=html_convert_cards(cards))

def parse_card_prices(card_prices):
    parsed_card_prices = []

    # Remove the euro and the whitespace from the price
    # The card price might be null, if so continue
    for card_price in card_prices:
        if not card_price:
            continue
        daw = str(card_price)
        daw = daw.strip("€").strip()
        daw = daw.replace(",",".")
        daw = float(daw)
        parsed_card_prices.append(daw)

    return parsed_card_prices

def html_convert_cards(cards):
    data = ""
    for card in cards:
        prices = card["prices"]
        parsed_prices = []

        for price in prices:
            parsed_prices.append(str(price))

        min_price = min(card["prices"])
        avg_price = mean(card["prices"])
        data = data + card["name"] + ": " + "Average price: {:.2f}".format(avg_price)\
            + " Minimum price: {}".format(min_price) + " All prices: " +\
            ", ".join(parsed_prices) + "<br>"


    print(data)
    return data


def parse_request(cards_requested):
    cards_requested = cards_requested.lower().splitlines()
    return cards_requested

def search_card(card_name):
    # Download the search page
    payload = {"mainPage": "showSearchResult", "searchFor": card_name}
    URL = "https://it.magiccardmarket.eu/"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.10 Safari/537.36'}
    r = requests.get(URL , params=payload, headers=HEADERS)

    # Code for 1-page-card
    if "Products" in r.url:
        single_card_href = r.url.split(".eu")[1]
        return [single_card_href]

    card_hrefs = parse_search_page(r.text, card_name)
    return card_hrefs

def parse_search_page(body, card_name):
    parsed_card_hrefs = []

    d = pq(body, parser="html")
    card_hrefs = d("tbody > tr > td.col_3 > a").items()

    for href in card_hrefs:
        if href.text().lower() == card_name:
            parsed_card_hrefs.append(href.attr("href"))

    return parsed_card_hrefs

def get_card_prices(card_hrefs):
    card_urls = []
    for card_href in card_hrefs:
        card_url = "https://it.magiccardmarket.eu"
        card_url += card_href
        card_urls.append(card_url)

    card_prices = concurrent_download(card_urls)
    return card_prices

def concurrent_download(urls):
    q = Queue()
    threads = []

    card_prices = []
    responses = []

    def downloader():
        while True:
            url = q.get()
            if url is None:
                break
            res = requests.get(url)
            responses.append(res.text)
            q.task_done()

    # There will be as many threads as urls
    # Currently the cuncurrent download happens on a singe card
    for url in urls:
        q.put(url)
        t = Thread(target=downloader)
        t.start()
        threads.append(t)

    q.join()
    for url in urls:
        q.put(None)

    for t in threads:
        t.join()

    for res in responses:
        card_prices.append(parse_price_page(res))

    return card_prices

def parse_price_page(body):
    d = pq(body, parser="html")
    card_price = d("#Dettagliprodotto > div > div.prodDetails > div:nth-child(3) > table > tbody > tr.row_Even.row_2 > td.outerRight.col_Odd.col_1.cell_2_1").text()
    if card_price is not None:
        return card_price
    return False

if __name__ == '__main__':
    app.run()
