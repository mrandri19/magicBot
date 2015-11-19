import unittest
import sys
sys.path.insert(0, "../src/")
import crawler
class TestCrawler(unittest.TestCase):
    def test_parse_card_prices(self):
        unparsed = ['34,16 €', '34,25 €']
        res = crawler.parse_card_prices(unparsed)
        self.assertEqual(res, [34.16, 34.25])
        return
    def test_html_convert_cards(self):
        return

    def test_get_card_edition(self):
        urls = ["/Products/Singles/Archenemy/Rancor", \
                "/Products/Singles/Planechase+2012/Rancor",\
                "/Products/Singles/WCD+1999%3A+Matt+Linde/Rancor"
                ]
        correct = ["Archenemy", "Planechase 2012", "WCD 1999: Matt Linde"]

        res = crawler.get_card_edition(urls)
        self.assertEqual(res, correct)
        return


if __name__ == '__main__':
    unittest.main()
