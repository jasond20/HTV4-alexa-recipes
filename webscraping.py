import requests
import traceback
from lxml import html

link = 'https://www.allrecipes.com/recipe/273231/coconut-tres-leches-cake/?internalSource=similar_recipe_banner&referringId=275698&referringContentType=Recipe&clickId=simslot_1'
pageContent=requests.get(link)

tree = html.fromstring(pageContent.content)
i =1
contentAvailible = True

ingredients = []
steps = []

#read steps
while(True):
    try:
        xPath = '//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ol/li[%x]/span/text()'%i
        i += 1
        step = tree.xpath(xPath)

        if len(step) == 0:
            break
        steps.append(step)
        print(step)

    except:
        traceback.print_exc()
        break
i =1
#ingredients list
while(True):
    try:
        xPath = '// *[ @ id = "lst_ingredients_1"] / li[%x] / label / span / text()'%i
        i+=1
        ingredient = tree.xpath(xPath)
        if len(ingredient) == 0:
            break
        ingredients.append(ingredient)
        print(ingredient)

    except:
        break

prepTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[2]/time/span/span/text()')
print(prepTime)

cookTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[3]/time/span/span/text()')
print(cookTime)

readyIn = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[4]/time/span/span/text()')
print(readyIn)
