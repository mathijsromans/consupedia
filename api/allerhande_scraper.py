import re
from api import cache
import logging

logger = logging.getLogger(__name__)

regex_unit = re.compile('data-quantity-unit-singular="(.*?)"')
regex_quantity = re.compile('data-quantity="(\d+)"')
regex_additional = re.compile('data-additional-info="(.*?)"')
regex_ingredient = re.compile('data-description-singular="(.*?)"')
regex_recipe_item_list = re.compile('<ul class="list shopping ingredient-selector-list">(.*?)</ul>', re.DOTALL)
regex_recipe_item = re.compile('<li itemprop="ingredients">(.*?)</li>', re.DOTALL)
regex_preparation_time = re.compile('<div class="icon icon-time"></div>(\d+).*?</li>', re.DOTALL)
regex_name = re.compile('<meta property="twitter:title" content="(.*?)">', re.DOTALL)
regex_number_persons = re.compile('<div class="icon icon-people"></div><span>.*?(\d+).*?</span></li>', re.DOTALL)
regex_recept_url = re.compile('/allerhande/recept/R-R(.*?)/', re.DOTALL)

# data-phone-src="https://static.ah.nl/static/recepten/img_088124_890x594_JPG.jpg"
regex_picture = re.compile('data-phone-src="(.*?)"', re.DOTALL)

# def get_recipe_ids_from_page(ah_url):
#     response = requests.get(ah_url)
#     if response.status_code != 200:
#         return '', ''
#     matches = regex_recept_url.findall(response.text)
#     matches = list(set(matches))
#     ids = []
#     for match in matches:
#         ids.append('R-R' + match)
#     return ids


def get_recipe_page_html(recipe_id):
    url = 'https://www.ah.nl/allerhande/recept/' + recipe_id
    result = cache.query(url, params={}, headers={}, result_type=cache.ResultType.HTML)
    return result, url


def get_recipe(recipe_id):
    text, url = get_recipe_page_html(recipe_id)
    logger.info(text)
    recipe_items = get_recipe_items(text)
    logger.info(str(recipe_items))
    preparation_time_in_min = get_preparation_time_min(text)
    number_persons = get_number_persons(text)
    name = get_name(text)
    picture_url = get_picture(text)
    recipe = {
        'name': name,
        'url': url,
        'picture_url': picture_url,
        'recipe_items': recipe_items,
        'preparation_time_in_min': preparation_time_in_min,
        'number_persons': number_persons
    }
    return recipe


def get_name(page_html_text):
    matches = regex_name.findall(page_html_text)
    return matches[0]


def get_number_persons(page_html_text):
    matches = regex_number_persons.findall(page_html_text)
    return int(matches[0])


def get_picture(page_html_text):
    matches = regex_picture.findall(page_html_text)
    return matches[0]


def get_recipe_items(page_html_text):
    matches = regex_recipe_item_list.findall(page_html_text)
    recipe_item_list = matches[0]
    matches = regex_recipe_item.findall(recipe_item_list)
    recipe_items = []
    for match in matches:
        name = ''
        unit = ''
        quantiy = 0

        matches = regex_quantity.findall(match)
        if matches:
            quantiy = int(matches[0])

        matches = regex_ingredient.findall(match)
        if matches:
            name = matches[0]

        matches = regex_unit.findall(match)
        if matches:
            unit = matches[0]

        matches = regex_additional.findall(match)
        unit_not_so_good = unit == 'pak' or unit == 'zakken' or unit == 'zak'
        if unit_not_so_good and matches:
            addit = matches[0].split(' ')
            if len(addit) == 2:
                quantiy = int(addit[0])
                unit = addit[1]
            elif len(addit) == 3 and addit[0] == 'a':
                quantiy = int(addit[1])
                unit = addit[2]

        recipe_items.append([quantiy, unit, name])
    return recipe_items


def get_preparation_time_min(page_html_text):
    matches = regex_preparation_time.findall(page_html_text)
    try:
        prep_time = int(matches[0])
    except ValueError:
        prep_time = None
    return prep_time
