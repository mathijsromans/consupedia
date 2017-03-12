import requests
import re
from html.parser import HTMLParser

class AllerhandeScraper:
    # ingredientenlijst = [
    #     [4, 'uien']
    #     [500, g, 'preien'],
    #     40, g, boter],
    #     2, el, olijfolie],
    #     1, el, gedroogde tijm],
    #     2, blaadjes, laurierblaadjes],
    #     198, g, corned beef],
    #     2, kg, gezeefde tomaten],
    #     1, kg, half-om-halfgehakt]]
    #
    # def get_search_result(self, search_term):
    #     params = {
    #         'SearchTerm': search_term,
    #         'PageNumber': 1
    #     }
    #     results = []
    #
    #     response = requests.get("https://www.jumbo.com/producten", params)
    #     regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
    #     matches = regex.findall(response.text)
    #
    #     for match in matches:
    #         results.append({ match[0]: str(match[1] + '' + match[2])})
    #
    #     params = {
    #         'SearchTerm': search_term,
    #         'PageNumber': 2
    #     }
    #     response = requests.get("https://www.jumbo.com/producten", params)
    #     regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
    #     matches = regex.findall(response.text)
    #
    #     for match in matches:
    #         results.append({ match[0]: str(match[1] + '' + match[2])})
    #
    #     params = {
    #         'SearchTerm': search_term,
    #         'PageNumber': 3
    #     }
    #     response = requests.get("https://www.jumbo.com/producten", params)
    #     regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
    #     matches = regex.findall(response.text)
    #
    #     for match in matches:
    #         results.append({ match[0]: str(match[1] + '' + match[2])})
    #
    #
    #     return results
