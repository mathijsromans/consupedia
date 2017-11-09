import requests
import json
from .models import QuestionMarkQuery
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.1/'

def search_product(search_name):
    start = time.time()
    params = {
        'q': search_name,
        'per_page': 100
    }
    params_as_string = json.dumps(params)
    logger.info('search_product @a: ' + str(time.time() - start))
    query, created = QuestionMarkQuery.objects.get_or_create(params_as_string=params_as_string)
    logger.info('search_product @b: ' + str(time.time() - start))
    if created:
        response = requests.get(BASE_URL + 'products/', params)
        logger.info('New query: ' + response.url)
        query.json = json.dumps(response.json())
        # with open('query_' + params_as_string + '.json', 'w') as f:
        #     f.write(query.json)
        query.save()
    return json.loads(query.json)
