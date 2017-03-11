import requests
import json
from .models import QuestionMarkQuery

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.1/'

def search_product(search_name):
    params = {
        'q': search_name
    }
    query, created = QuestionMarkQuery.objects.get_or_create(q_product_name = search_name)
    if created:
        response = requests.get(BASE_URL + 'products/', params)
        print('New query: ' + response.url)
        query.json = json.dumps(response.json())
        query.save()
    return json.loads(query.json)
