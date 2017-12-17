import re
from .models import JumboQuery
import logging
import time
from api import cache

logger = logging.getLogger(__name__)

# note that (?s) sets the ". matches everything including newline" flag
regex_product = '(?s)<h3 data-jum-action.*?quickView">(.*?)</a></h3>.*?jum-price-format">(.*?)<sup>(.*?)</sup>.*?jum-pack-size">(.*?)</span>';

def search_product(search_term):
    MAX_PAGES = 10
    results = []
    for page_number in range(0, MAX_PAGES):
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
        query.html = cache.query("https://www.jumbo.com/producten", params=params, headers={}, result_type=cache.ResultType.HTML)
        query.save()

    regex = re.compile(regex_product)
    matches = regex.findall(query.html)

    return matches
