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


if __name__ == '__main__':
    unittest.main()
