/*
 * Webserver -> Express
 * textbox con le carte che aggiorna la pagina dando i dati in un jumbotron
 * get request che ritorna la pagina creata con jade
 * quando viene fatta la get request viene eseguito lo script che CRAWLA
 * prendi input dalla textbox, formattali
 * passali allo script attraverso POST
 * per ogni inserzione, getta la pagina
 * https://it.magiccardmarket.eu/?mainPage=showSearchResult&searchFor=NOMECARTA
 * per ogni inserzione della pagina getta la pagina del singolo item
 * ottieni il prezzo medio
 */

var cheerio = require('cheerio');
var request = require('request');
var querystring = require('querystring');

var express = require('express');
var app = express();

function crawl(cardname, callback) {
    var url = 'https://it.magiccardmarket.eu/?mainPage=showSearchResult&searchFor='+encodeURIComponent(cardname);
    var options = {
        url: url,
        headers: {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.10 Safari/537.36'
        }
    };
    console.log('Requesting: '+url);
    request(options , function(error, response, body) {
        console.log(error+'     '+response.statusCode);
        if (!error && response.statusCode == 200) {
            console.log('Downloaded page');
            var $ = cheerio.load(body);
            $();
            callback('dawdwawdawd');
        }
    });
}

app.set('view engine', 'jade');

app.get('/daw', function(req, res) {
    crawl('Mox Opal', function(data) {
        res.send(data);
    });
});
app.get('/', function (req, res) {
    var results = 'EXAMPLE: Mox Opal, 34.12';
    res.render('index', {
        results: results 
    });
});
app.post('/', function(req, res){
    var results = 'TEST';
    results = crawl();
    res.render('index', {
        results: results
    });
});

app.listen(8080);
