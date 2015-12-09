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

html = urllib.urlopen('http://www.budgetbytes.com/2015/12/30-minute-posole/').read()
recipe = BeautifulSoup(html)
recipe = recipe.find_all('li', class_='ingredient')
ingredients_list = []
for item in recipe:
    item = fix_encoding(item.text)
    item = transform_ingredient(str(item))
    ingredients_list.append(item)

print ingredients_list



