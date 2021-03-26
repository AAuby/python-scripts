import requests
from lxml import etree


base_url = "http://db.foodmate.net/yingyang/"
food_meta = []

category = open("category.txt", "w+", encoding="UTF-8")

category_resp = requests.get(base_url)
category_resp_parse = etree.HTML(category_resp.text)

for element in category_resp_parse.xpath('//div[@id="main2"]//a'):
    if element.text == "xlfcnkvf":
        continue
    detail_resp = requests.get(f'{base_url}{element.get("href")}')
    detail_resp_parse = etree.HTML(detail_resp.text)
    category.write("\n")
    category.write(element.text+"\n")
    category.write("=====================================================================================\n")
    for a in detail_resp_parse.xpath('//div[@id="dibu"]//a'):
        link, content = (a.get("href"), a.text)
        food_resp = requests.get(f'{base_url}{link}')
        food_resp_parse = etree.HTML(food_resp.text)
        category.writelines(content+"\n")
        food = {
            "food_name": content,
            "detail": {}
        }
        for f in food_resp_parse.xpath('//div[@class="list"]'):
            food["detail"][f.getchildren()[0].text] = f.xpath('text()')[0] if f.xpath('text()') else 0
        food_meta.append(food)
category.close()
