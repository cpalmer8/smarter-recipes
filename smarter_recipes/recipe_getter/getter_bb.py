from bs4 import BeautifulSoup
import urllib
import re
import couchdb

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

#gets a list of the 'first' 10 urls, corresponding to updated blog posts
#past 10 = older posts on different parts of the page
#ideally this would not be managed with a nested loop
#also needs socket improvement/parallelization per cProfile analysis
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

#inserting data into couchdb
#note: this is an early prototype
#for this to work we'd need to map/reduce on docs by "day"/chunk of 10
def insert_data(final_data):
    server = couchdb.Server()
    db = server['recipe_ingredients']
    doc = final_data
    db.save(doc)

#gets recipes & ingredients, puts them in a dict
def open_recipes():
    recipe_urls = get_urls()
    final_data = {}
    for url in recipe_urls:
        recipe_ingredients = get_ingredients(url)
        if (recipe_ingredients):
            final_data[url] = recipe_ingredients
    insert_data(final_data)




