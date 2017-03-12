import requests
import re
from html.parser import HTMLParser

regex_unit = re.compile('data-quantity-unit-singular="(.*?)"')
regex_quantity = re.compile('data-quantity="(\d+)"')
regex_ingredient_name = re.compile('data-description-singular="(.*?)"')
regex_ingredients_list = re.compile('<ul class="list shopping ingredient-selector-list">(.*?)</ul>', re.DOTALL)
regex_ingredient_item = re.compile('<li itemprop="ingredients">(.*?)</li>', re.DOTALL)
regex_preparation_time = re.compile('<div class="icon icon-time"></div>(\d+).*?</li>', re.DOTALL)
regex_name = re.compile('<meta property="twitter:title" content="(.*?)">', re.DOTALL)
regex_number_persons = re.compile('<div class="icon icon-people"></div><span>.*?(\d+).*?</span></li>', re.DOTALL)


def get_recipe_page_html(recipe_id):
    url = 'https://www.ah.nl/allerhande/recept/' + recipe_id
    response = requests.get(url)
    if response.status_code != 200:
        return '', ''
    return response.text, url


def get_recipe(recipe_id):
    text, url = get_recipe_page_html(recipe_id)
    ingredients = get_recipe_ingredients(text)
    preparation_time_in_min = get_preparation_time_min(text)
    number_persons = get_number_persons(text)
    name = get_name(text)
    recipe = {
        'name': name,
        'url': url,
        'ingredients': ingredients,
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


def get_recipe_ingredients(page_html_text):
    matches = regex_ingredients_list.findall(page_html_text)
    ingredient_list = matches[0]
    matches = regex_ingredient_item.findall(ingredient_list)
    ingredients = []
    for match in matches:
        name = ''
        unit = ''
        quantiy = ''
        matches = regex_quantity.findall(match)
        if matches:
            quantiy = int(matches[0])
        matches = regex_ingredient_name.findall(match)
        if matches:
            name = matches[0]
        matches = regex_unit.findall(match)
        if matches:
            unit = matches[0]
        ingredients.append([quantiy, unit, name])
    return ingredients


def get_preparation_time_min(page_html_text):
    matches = regex_preparation_time.findall(page_html_text)
    try:
        prep_time = int(matches[0])
    except ValueError:
        prep_time = None
    return prep_time
