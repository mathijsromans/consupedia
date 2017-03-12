import requests
import re
from html.parser import HTMLParser
from .models import JumboQuery

regex_product = '<h3 data-jum-action.*quickView">(.*)</a></h3>\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*jum-price-format">(.*)<sup>(.*)</sup>.*jum-pack-size">(.*)</span>';

def search_product(search_term):
    MAX_PAGES = 10
    results = []
    for page_number in range(1, MAX_PAGES):
        matches = get_search_result(search_term, page_number)

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


def get_search_result(search_term, page_number):
    params = {
        'SearchTerm': search_term,
        'PageNumber': page_number
    }

    query, created = JumboQuery.objects.get_or_create(q_product_name = search_term + str(page_number))
    if created:
        response = requests.get("https://www.jumbo.com/producten", params)
        query.html = response.text
        query.save()

    regex = re.compile(regex_product)
    matches = regex.findall(query.html)

    return matches
