import datetime
import requests
from config import SILPOshops

def get_silpo(body):
    URL = "https://api.catalog.ecom.silpo.ua/api/2.0/exec/EcomCatalogGlobal"
    headers = {"content-type": "application/json"}
    shop_id = body['shop_id']
    category = body['name']
    body = body['body']
    r = requests.post(URL, json=body, headers=headers)
    items = []
    for i in r.json()["items"]:
        title = i["name"]
        storeQuantity = i["storeQuantity"]
        unit = i["unit"]
        status = 0
        if storeQuantity != 0:
            status = 1
        price = i["price"]
        old_price = i["oldPrice"]
        shop_item_id = i['id']
        image = i["mainImage"]
        link = f'https://shop.silpo.ua/detail/{i["id"]}'
        weight = i["unit"]
        items.append(
                {
                    "title": title,
                    "price": price,
                    "old_price": old_price,
                    "weight": weight,
                    "image": image,
                    "link": link,
                    # "avg_price": price_for_kl,
                    "category": category,
                    "shop": "silpo",
                    "shop_id": int(shop_id),
                    "shop_item_id": shop_item_id,
                    "history": [{'Date': datetime.datetime.now(), 'Price': price}],
                    "update_time": datetime.datetime.now(),
                    "status": status
                }
            )

    return items





def get_categories_silpo():
    bodies = []
    for silpo in SILPOshops:
        body = {
        "method": "GetCategories",
        "data": {
            "merchantId": 1,
            "basketGuid": "3e08f7cc-0932-49ea-baae-5986f92c271c",
            "deliveryType": 1,
            "filialId": silpo
            }
        }
        URL = "https://api.catalog.ecom.silpo.ua/api/2.0/exec/EcomCatalogGlobal"

        headers = {"content-type": "application/json"}
        r = requests.post(URL, json=body, headers=headers)

        for i in r.json()['tree']:
            if i['parentId']:
                break
            bodies.append({'name': i['name'],
                               'body':{
                                   "data": {
                                                   "CategoryFilter": [],
                                                   "From": 1,
                                                   "MultiFilters": {},
                                                   "Promos": [],
                                                   "RangeFilters": {},
                                                   "To": 999,
                                                   "UniversalFilters": [],
                                                   "basketGuid": "",
                                                   "businessId": 1,
                                                   "categoryId": i['id'],
                                                   "deliveryType": 1,
                                                   "filialId": silpo,
                                               },
                                               "method": "GetSimpleCatalogItems",
                               }, 'shop_id': silpo})

    return bodies
