import requests
import re
import json
from html.parser import HTMLParser
from .models import AHQuery


def search_product(search_term):
    query, created = AHQuery.objects.get_or_create(q_product_name = search_term)
    if created:
        URL = 'https://www.ah.nl/service/rest/delegate?url=/zoeken?rq='
        fake_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(URL + search_term, headers = fake_headers)
        query.json = json.dumps(response.json())
        query.save()

    json_products =  json.loads(query.json)  


    results = []
    items = json_products['_embedded']['lanes'][6]['_embedded']['items']
    for item in items:
        if '_embedded' in item:
            ah_product = item['_embedded']['product']
            results.append({ 
                'name' : ah_product['description'], 
                'price': str(ah_product['priceLabel']['now']).replace('.', ''), 
                'size': ah_product['unitSize']
            })
    return results
