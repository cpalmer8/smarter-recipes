from bs4 import BeautifulSoup
import urllib
import re
import couchdb
import yaml

#budget bytes recipes come with dollar amounts, we want to remove those
def transform_ingredient(ingredient):
    ingredient = re.sub(r'[\$][0-9]*\.[0-9]*', "", ingredient)
    return ingredient

#fix encoding so unicode fractions won't break the script
def fix_encoding(item):
    maxord = max(ord(char) for char in item)
    if maxord < 128:
        return item
    else:
        newtext = item.encode('utf-8', 'replace')
        return newtext

#get array of ingredients from each url
def get_ingredients(url, ingredient_selector, ingredient_class):
    html = urllib.urlopen(url).read()
    recipe = BeautifulSoup(html)
    recipe = recipe.find_all(ingredient_selector, class_=ingredient_class)
    ingredients_list = []
    for item in recipe:
        item = fix_encoding(item.text)
        item = transform_ingredient(str(item))
        ingredients_list.append(item)
    return ingredients_list

#gets a list of the 'first' 10 urls, corresponding to updated blog posts
#past 10 = older posts on different parts of the page
#ideally this would not be managed with a nested loop
#also needs socket improvement/parallelization per cProfile analysis
def get_urls(url, link_selector, link_class):
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    urls = soup.find_all(link_selector, class_=link_class, limit=10)
    recipe_urls = []
    for url in urls:
        for a in url:
            recipe_urls.append(a["href"])
    return recipe_urls

#inserting data into couchdb
#note: this is an early prototype
#for this to work we'd need to map/reduce on docs by "day"/chunk of 10
def insert_data(final_data):
    server = couchdb.Server()
    db = server['recipe_ingredients']
    doc = final_data
    db.save(doc)

def ingest_yaml(key):
    with open('recipe_config.yml', 'r') as cfg:
        doc = yaml.load(cfg)
        url = doc[key]['url']
        link_selector = doc[key]['link_selector']
        link_class = doc[key]['link_class']
        ingredient_selector = doc[key]['ingredient_selector']
        ingredient_class = doc[key]['ingredient_class']
    open_recipes(url, link_selector, link_class, ingredient_selector, ingredient_class)

#gets recipes & ingredients, puts them in a dict
def open_recipes(url, link_selector, link_class, ingredient_selector, ingredient_class):
    recipe_urls = get_urls(url, link_selector, link_class)
    final_data = {}
    for recipe in recipe_urls:
        recipe_ingredients = get_ingredients(recipe, ingredient_selector, ingredient_class)
        if (recipe_ingredients):
            final_data[recipe] = recipe_ingredients
    insert_data(final_data)

