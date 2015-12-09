from bs4 import BeautifulSoup
import urllib
import re

def transform_ingredient(ingredient):
    ingredient = re.sub(r'[\$][0-9]*\.[0-9]*', "", ingredient)
    return ingredient

def fix_encoding(item):
    maxord = max(ord(char) for char in item)
    if maxord < 128:
        return item
    else:
        newtext = item.encode('utf-8', 'replace')
        return newtext

def get_ingredients(url):
    html = urllib.urlopen(url).read()
    recipe = BeautifulSoup(html)
    recipe = recipe.find_all('li', class_='ingredient')
    ingredients_list = []
    for item in recipe:
        item = fix_encoding(item.text)
        item = transform_ingredient(str(item))
        ingredients_list.append(item)
    return ingredients_list

def get_urls():
    html = urllib.urlopen('http://budgetbytes.com').read()
    soup = BeautifulSoup(html)
    dates = soup.find_all('time', class_='entry-time')
    dates_list = []
    for date in dates:
        dates_list.append(str(date.text))
    urls = soup.find_all('h2', class_='entry-title', limit=10)
    recipe_urls = []
    for url in urls:
        for a in url:
            recipe_urls.append(a["href"])
    return recipe_urls

def open_recipes():
    recipe_urls = get_urls()
    final_data = {}
    for url in recipe_urls:
        recipe_ingredients = get_ingredients(url)
        final_data[url] = recipe_ingredients
    print final_data


open_recipes()


