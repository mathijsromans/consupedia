import json
from .models import *
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
        products_dict = search_by_string(params)
        if products_dict['total'] != 0:
            break
        params['q'] = " ".join(params['q'].split(" ")[1:])  # remove first word, e.g. "gedroogde tijm" -> "tijm"
    results = []
    for product_dict in products_dict['products']:
        qm_id = int(product_dict['id'])
        entry, created = QuestionmarkEntry.objects.get_or_create(id=qm_id)
        entry.name = product_dict['name']
        map_brand(entry, product_dict)
        map_scores(entry, product_dict)
        map_urls(entry, product_dict)
        map_certificates(entry, product_dict)
        map_nutrients(entry, product_dict)
        entry.save()
        results.append(entry)
    return results


def search_by_string(params):
    params_as_string = json.dumps(params)
    query, created = QuestionMarkQuery.objects.get_or_create(params_as_string=params_as_string)
    if created:
        query.json = json.dumps(cache.query(BASE_URL + 'products/', params=params, headers={}, result_type=cache.ResultType.JSON))
        # with open('query_' + params_as_string + '.json', 'w') as f:
        #     f.write(query.json)
        query.save()
    result = json.loads(query.json)
    # logger.info('RESULT IS ' + str(result))
    return result


def map_brand(entry, product_dict):
    if product_dict['brand'] and product_dict['brand']['name']:
        entry.brand = product_dict['brand']['name']


def map_urls(entry, product_dict):
    if 'image_urls' in product_dict:
        urls = product_dict['image_urls']
        for url in urls:
            if 'thumb' in url:
                entry.thumb_url = url['thumb']
                return


def map_scores(entry, product_dict):
    theme_scores = product_dict["theme_scores"]
    for score in theme_scores:
        if score["theme_key"] == "environment":
            entry.score_environment = score["score"]
        elif score["theme_key"] == "social":
            entry.score_social = score["score"]
        elif score["theme_key"] == "animals":
            entry.score_animals = score["score"]
    # entry.score_personal_health = product_dict["personal_health_score"]


def map_certificates(entry, product_dict):
    for certificate in product_dict["certificates"]:
        id = int(certificate['id'])
        qm_certificate, created = QuestionmarkCertificate.objects.get_or_create(id=id)
        qm_certificate.name = certificate['name']
        qm_certificate.image_url = certificate['image_url']
        for theme in certificate['themes']:
            qm_theme, created = QuestionmarkTheme.objects.get_or_create(name=theme)
            qm_certificate.themes.add(qm_theme)
        qm_certificate.save()
        entry.certificates.add(qm_certificate)


def map_nutrients(entry, product_dict):
    for nutrient in product_dict["product_nutrients"]:
        if nutrient['code'] == 'energy':
            entry.energy_in_kj_per_100_g = nutrient['value']
        elif nutrient['code'] == 'protein':
            entry.protein_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'carbohydrates':
            entry.carbohydrates_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'sugar':
            entry.sugar_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'fat_saturated':
            entry.fat_saturated_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'fat_total':
            entry.fat_total_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'salt':
            entry.salt_in_g_per_100_g = nutrient['value']
        elif nutrient['code'] == 'fiber':
            entry.fiber_in_g_per_100_g = nutrient['value']
