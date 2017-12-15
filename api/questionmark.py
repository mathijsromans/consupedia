import requests
import json
from .models import QuestionMarkQuery
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.2/'


def search_product(search_name):
    params = {
        'q': search_name,
        'per_page': 100
    }
    while params['q']:
        result = search_by_string(params)
        if result['total'] != 0:
            break
        params['q'] = " ".join(params['q'].split(" ")[1:])  # remove first word, e.g. "gedroogde tijm" -> "tijm"
    return result


def search_by_string(params):
    logger.info('SEARCHING FOR ' + str(params))
    params_as_string = json.dumps(params)
    query, created = QuestionMarkQuery.objects.get_or_create(params_as_string=params_as_string)
    if created:
        response = requests.get(BASE_URL + 'products/', params)
        logger.info('New query: ' + response.url)
        query.json = json.dumps(response.json())
        # with open('query_' + params_as_string + '.json', 'w') as f:
        #     f.write(query.json)
        query.save()
    result= json.loads(query.json)
    # logger.info('RESULT IS ' + str(result))
    return result
