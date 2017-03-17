import requests
import json
from .models import QuestionMarkQuery

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.1/'

def search_product(search_name):
    params = {
        'q': search_name,
        'per_page': 100
    }
    params_as_string = json.dumps(params)
    query, created = QuestionMarkQuery.objects.get_or_create(params_as_string = params_as_string)
    if created:
        response = requests.get(BASE_URL + 'products/', params)
        print('New query: ' + response.url)
        query.json = json.dumps(response.json())
        query.save()
    return json.loads(query.json)
