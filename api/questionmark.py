import json
from .models import QuestionMarkQuery
import logging
import time
from api import cache

logger = logging.getLogger(__name__)

# documentation: http://www.thequestionmark.org/beta-api/
BASE_URL = 'https://api-c.thequestionmark.org/api/v1.2/'


def search_product(search_name):
    # 500 is max per page for questionmark
    params = {
        'q': search_name,
        'per_page': 500
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
        query.json = json.dumps(cache.query(BASE_URL + 'products/', params=params, headers={}, result_type=cache.ResultType.JSON))
        # with open('query_' + params_as_string + '.json', 'w') as f:
        #     f.write(query.json)
        query.save()
    result= json.loads(query.json)
    # logger.info('RESULT IS ' + str(result))
    return result

def get_all():
    page = 0
    results_found = True
    while results_found:
        page = page + 1
        results_found = store_results(page)

def store_results(page):
    params = {
        'per_page': 500,
        'page': page
    }

    params_as_string = json.dumps(params)
    json_result = cache.do_query(BASE_URL + 'products/', params=params, headers={}, result_type=cache.ResultType.JSON)
    string_result = json.dumps(json_result)

    filename = 'qm_' + str(page) + '.json'
    with open(filename, 'x') as out:
        out.write(string_result)

    results_found = len(json_result['products']) > 0

    return results_found

