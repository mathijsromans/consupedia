import requests
import re
from html.parser import HTMLParser

class JumboScraper:
    def get_search_result(self, search_term):
        params = {
            'SearchTerm': search_term,
            'PageNumber': 1
        }
        results = []

        response = requests.get("https://www.jumbo.com/producten", params)
        regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
        matches = regex.findall(response.text)

        for match in matches:
            results.append({ match[0]: str(match[1] + '' + match[2])})

        params = {
            'SearchTerm': search_term,
            'PageNumber': 2
        }
        response = requests.get("https://www.jumbo.com/producten", params)
        regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
        matches = regex.findall(response.text)

        for match in matches:
            results.append({ match[0]: str(match[1] + '' + match[2])})

        params = {
            'SearchTerm': search_term,
            'PageNumber': 3
        }
        response = requests.get("https://www.jumbo.com/producten", params)
        regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>')
        matches = regex.findall(response.text)

        for match in matches:
            results.append({ match[0]: str(match[1] + '' + match[2])})


        return results
