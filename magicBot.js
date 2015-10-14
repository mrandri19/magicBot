/*
 * Webserver -> Express
 * textbox con le carte che aggiorna la pagina dando i dati in un jumbotron
 * get request che ritorna la pagina creata con jade
 * quando viene fatta la get request viene eseguito lo script che CRAWLA
 * prendi input dalla textbox, formattali
 * passali allo script attraverso POST
 * per ogni inserzione, getta la pagina
 * https://it.magiccardmarket.eu/?mainPage=showSearchResult&searchFor=NOMECARTA
 *
 * per ogni inserzione della pagina getta la pagina del singolo item
 * ottieni il prezzo medio
 */
var RSVP = require('RSVP');
var cheerio = require('cheerio');
var request = require('request');
var querystring = require('querystring');

var bodyParser = require('body-parser');
var express = require('express');
var app = express();
var bodyParser = require('body-parser');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
// in latest body-parser use like bellow.
app.use(bodyParser.urlencoded({ extended: false }));

function parseData(data, callback) {
    var parsedData = data.split('\n');
    return callback(parsedData);
}

function parsePrices(i, names, body, $, callback) {

    var promise = new RSVP.Promise(function(series_callback) {
        $ = cheerio.load(body);

        //Remove half of the string to remove the double repeated price
        var tmp = $('table.availTable tr td.cell_2_1').text();
        tmp = tmp.slice(tmp.length/2);
        names.price[i] = tmp;

        console.log('Checking price: '+names.price[i]);
        resolve();
    }
}

//TODOOOO: this function is fucking long, boy
function crawl(cardname, callback) {
    //Building the url for the search page
    var searchUrl = 'https://it.magiccardmarket.eu/?mainPage=showSearchResult&searchFor=';
    var url = searchUrl + encodeURIComponent(cardname);
    var header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.10 Safari/537.36'
    };
    var options = {
        url: url,
        headers: header
    };

    console.log('Requesting: '+url);
    request(options , function(error, response, body) {

        if (!error && response.statusCode === 200) {
            console.log('Downloaded search page');

            var names = {
                text: [],
                href: [],
                price: [],
                ok: true
            };

            var $ = cheerio.load(body);
            console.log('Parsing the page');

            //Check if there are hrefs in the search page
            var href_lenght =  $('tbody > tr > td.col_3 > a').length;
            if (href_lenght < 1) {
                console.log('No hrefs found');
                return callback({ok: false});
            }
            console.log('Found ' + href_lenght + ' hrefs');

            //For each href compare its name with the cardname, after lowercasing it
            //if they match add the name and the href to the names object
            $('tbody > tr > td.col_3 > a').each(function(i, elem) {
                if(cardname.toLowerCase() === $(elem).text().toLowerCase()) {
                    console.log('Found a cardname');
                    names.text[i] = $(elem).text();
                    names.href[i] = $(elem).attr('href');
                }
            });

            //Reset cheerio
            $ = null;

            console.log(names);

            //If hrefs have been found
            if (names.href.length < 1) {
                console.log('No links found, returning false');
                return callback({ok: false});
            }

            names.href.forEach(function(link, i) {
                //Build the url and request
                var pricesUrl = "https://it.magiccardmarket.eu" + link;
                var prices_options = {
                    url: pricesUrl,
                    headers: header
                };

                console.log(i + ' Downloading: ' + link);
                request(prices_options, function(error, response, body) {

                    if (!error && response.statusCode === 200) {
                        parsePrices(i, names, body, $, callback);
                    } else {
                        console.log('Price page request returned error: '+ response.statusCode);
                        return callback({ok: false});
                    }

                });//End of request
            });//End of foreachLink

        } else {
            console.log('Search page request returned error: ' + error + " and statusCode: "+ response.statusCode);
            return callback({ok: false});
        }
    });
}

app.set('view engine', 'jade');

app.get('/', function (req, res) {
    console.log('Got: ' + res.method + ' request from: ' +req.connection.remoteAddress);
    var results = '';
    res.render('index', {
        results: results
    });
});

app.post('/', function(req, res){
    parseData(req.body.cards, function(cards) {
        console.log(cards);
        crawl(cards[0], function(data) {
            if (data.length < 0) {
                data = {ok: false};
            }
            console.log("Rendering .jade");
            res.render('index', {
                    results: data
            });
        });
    });
});

app.listen(8080);
