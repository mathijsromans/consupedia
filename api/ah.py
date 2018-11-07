import logging
import json
from .models import AHQuery, AHEntry
from api import cache

logger = logging.getLogger(__name__)


def search_product(search_term):
    logger.info('Starting AH query...')
    query, created = AHQuery.objects.get_or_create(q_product_name=search_term)
    if created:
        url = 'https://www.ah.nl/service/rest/delegate?url=/zoeken?rq='
        fake_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        result = cache.query(url + search_term, params={}, headers=fake_headers, result_type=cache.ResultType.JSON)
        query.json = json.dumps(result)
        query.save()

    logger.info('AH query done')
    json_products = json.loads(query.json)

    results = []
    items = []
    try:
        for lane in json_products['_embedded']['lanes']:
            if lane['type'] == 'SearchLane':
                items += lane['_embedded']['items']
    except KeyError as error:
        # This is not a real error, just the quickest way to see if there are items
        logger.info(error)
        return results
    for item in items:
        try:
            ah_product = item['_embedded']['product']
            price_str = str(ah_product['priceLabel']['now'])
            price = int(100*float(price_str))
            logger.info('Found AH item "' + ah_product['description']+'"')
            ah_id = ah_product['id']
            name = ah_product['description']
            size = ah_product['unitSize']
            entry, created = AHEntry.objects.update_or_create(
                ah_id=ah_id, defaults={'name': name, 'price': price, 'size': size})
            results.append(entry)
        except KeyError:
            pass  # Ignore, go to next item

    return results
