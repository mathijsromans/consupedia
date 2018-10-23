import re
from .models import JumboQuery, JumboEntry
import logging
import time
from api import cache

logger = logging.getLogger(__name__)

# note that (?s) sets the ". matches everything including newline" flag
regex_product = '(?s)data-jum-action.*?quickView">(.*?)</a></h3>.*?jum-price-format">(.*?)<sup>(.*?)</sup>.*?jum-pack-size">(.*?)</span>'
MAX_PAGES = 10

def search_product(search_term):
    results = []
    for page_number in range(0, MAX_PAGES):
        query = do_query(search_term, page_number)
        matches = get_matches(query.html)
        if not matches:
            break
        results += process_matches(matches)
    return results


def process_matches(matches):
    results = []
    for match in matches:
        logger.info('Adding Jumbo match {}'.format(match))
        name = match[0]
        price = int(str(match[1] + '' + match[2]))
        size = match[3]
        entry, created = JumboEntry.objects.update_or_create(
            name=name, defaults={'price': price, 'size': size})
        results.append(entry)
    return results


def do_query(search_term, page_number):
    params = {
        'SearchTerm': search_term,
        'PageNumber': page_number
    }

    query, created = JumboQuery.objects.get_or_create(q_product_name=search_term + str(page_number))
    if created:
        query.html = cache.query("https://www.jumbo.com/producten", params=params, headers={}, result_type=cache.ResultType.HTML)
        query.save()
    return query


def get_matches(html):
    regex = re.compile(regex_product)
    matches = regex.findall(html)
    logger.info('Searching Jumbo returns {} matches'.format(len(matches)))
    return matches
