import requests
import re
from html.parser import HTMLParser

def search_product(search_term):
    MAX_PAGES = 10
    for i in range(1, MAX_PAGES):
        params = {
            'SearchTerm': search_term,
            'PageNumber': i
        }
        results = []

        response = requests.get("https://www.jumbo.com/producten", params)
        regex = re.compile('<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>.*jum-pack-size">(.*)</span>')
        matches = regex.findall(response.text)

        if matches:
            for match in matches:
                results.append({ 
                    'name' : match[0], 
                    'price': str(match[1] + '' + match[2]),
                    'size': match[3]
                })
        else:
            break

    return results
