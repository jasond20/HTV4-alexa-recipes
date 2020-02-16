import requests
import traceback
from lxml import html

def food_scraping(link):
    pageContent=requests.get(link)
    tree = html.fromstring(pageContent.content)
    i = 1
    ingredients = []
    ingredientsXpath = ['//*[@id="lst_ingredients_1"]/li[%i]/label/span/text()',
                        '//*[@id="lst_ingredients_2"]/li[%i]/label/span/text()']
    xPathCounter = 0
    ingredientsListNum = 1
    steps = []
        #read steps
    while(True):
        try:
            xPath = '//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ol/li[%x]/span/text()'%i
            i += 1
            step = tree.xpath(xPath)
            step = str(step)[2:len(str(step))-32]
            if len(step) == 0:
                break
            steps.append(step)
            #print(step)
        except:
            #traceback.print_exc()
            break
    i = 1
    #ingredients list
    while(True):
        try:
            xPath = ingredientsXpath[xPathCounter]%i
            i += 1
            #print(xPath)
            ingredient = tree.xpath(xPath)
            ingredient =str(ingredient)[2:len(str(ingredient))-2]
            if ingredient == "Add all ingredients to the list":
                break
            if len(ingredient) == 0:
                xPathCounter+=1
                i =1
                if(xPathCounter>1):
                    break
            ingredients.append(ingredient)
            #print(ingredient)
        except:
            #traceback.print_exc()
            break
    prepTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[2]/time/span/span/text()')
    prepTime = str(prepTime)[2:len(str(prepTime))-2]
    #print(prepTime)
    prepTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[2]/time/span/text()')
    #print(prepTimeUnit)
    cookTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[3]/time/span/span/text()')
    #print(cookTime)
    cookTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[3]/time/span/text()')
    #print(cookTimeUnit)
    readyIn = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[4]/time/span/span/text()')
    #print(readyIn)
    readyInTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[4]/time/span/text()')
    #print(readyInTimeUnit)
    return steps, ingredients
#returns link and title of searched food
def food_search(food):
    link = 'https://www.allrecipes.com/search/results/?wt=%s&sort=re'%food
    pageContent=requests.get(link)
    tree = html.fromstring(pageContent.content)

    optionlink = tree.xpath('//*[@id="fixedGridSection"]/article[2]/div[2]/h3//a/@href')
    optionlink = str(optionlink)[2:len(str(optionlink))-2]
    optionname = tree.xpath('//*[@id="fixedGridSection"]/article[2]/div[2]/h3/a/span/text()')

    #print(optionlink)
    return optionlink, optionname
