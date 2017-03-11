import requests

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.1/'


def search_product(product_name):
    params = {
        'q': product_name
    }
    response = requests.get(BASE_URL + 'products/', params)
    # print(response.url)
    products_json = response.json()
    # print(json.dumps(products_json, sort_keys=True, indent=2))
    return products_json
