import time
import re
import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger

from config import ATBshops
import requests
ua = UserAgent()

def get_atb(atb_link):
    shop_id = atb_link['shop_id']
    atb_url = atb_link['link']
    page = 1
    last_page = 1
    items = []
    cookies = {'birthday': 'true',
               'store_id': f'{shop_id}'}
    while page <= last_page:
        response = requests.get(

            url=atb_url + str(page),
            headers={'user-agent': f'{ua.random}'},
            cookies=cookies,
            verify=False
        )
        soup = BeautifulSoup(response.content, "html.parser")
        if page == last_page:
            try:
                page_list = soup.find("ul", {"class": "product-pagination__list"})
                last_page = page_list.find_all("li")[-2]
                last_page = int(last_page.text)
            except Exception as ex:
                logger.debug(ex)
        catalog_list = soup.find("div", {"class": "catalog-list"})
        articles = catalog_list.find_all("article", class_=check_article)
        for article in articles:
            image = article.find("picture").find("source").get("srcset")
            old_price = None
            item_info = article.find("a", {"class": "blue-link"})
            title = item_info.get_text().replace(u'\xa0', ' ')


            link = "https://zakaz.atbmarket.com" + item_info.get("href")
            # logger.debug(title)
            price = float(article.find("data", {"class": "product-price__top"}).get("value"))
            unit = article.find("span", {"class": "product-price__unit"}).text
            unit = re.findall(r"/(\w+)", unit)[0]
            shop_item_id = int(article.find("div", {"class": "b-addToCart"}).get("data-productid"))
            old_price = article.find("data", {"class": "product-price__bottom"})
            # logger.debug(price)


            if old_price:
                old_price = old_price.get("value")
                # logger.debug(old_price)
            else:
                old_price = None
            # logger.debug("Объем: " + str(mass))
            weight = check_weight(title, unit)
            items.append(
                {
                    "title": title,
                    "price": price,
                    "old_price": old_price,
                    "weight": weight,
                    "image": image,
                    "link": link,
                    # "avg_price": avg_price,
                    "shop": "atb",
                    "category": atb_link['name'],
                    "shop_item_id": shop_item_id,
                    "shop_id": int(shop_id),
                    "history": [{'Date': datetime.datetime.now(), 'Price': price}],
                    "update_time": datetime.datetime.now(),
                    "status": 1
                }
            )






        time.sleep(1)
        page += 1
    return items


def check_weight(title, unit_shop):
    mass = None
    unit = None
    try:

        if re.search(r"\d,\d", title) or re.search(r"\d\.\d", title):
            digits = re.findall(r"\d+", title)
            mass = float(".".join(digits[0:2]))

        else:
            mass = int(re.findall(r"\d+", title)[0])

        if re.search(r"\dшт", title) or re.search(r"\d шт", title):
            unit = "шт"

        elif re.search(r"\dмл", title) or re.search(r"\d мл", title):
            # mass /= 1000
            unit = "мл"
        elif re.search(r"\dл", title) or re.search(r"\d л", title):
            unit = "л"
        elif re.search(r"\dкг", title) or re.search(r"\d кг", title):
            unit = "кг"
        elif re.search(r"\dг", title) or re.search(r"\d г", title):
            unit = "г"
            # mass /= 1000
    except:
        pass
    if (not mass and not unit) or not unit:
        mass = 1
        unit = unit_shop
    logger.debug(f"{title} | {mass} {unit} | {unit_shop}")
    return f"{mass}{unit}"



def check_article(article):
    return re.compile("catalog-item").search(article)


def get_categories_atb():
    url = "https://zakaz.atbmarket.com"
    ban_catalog = ["Економія", "Новинки", "Акція 7 днів"]

    links = []
    for shop_id in ATBshops:
        cookies = {'store_id': f'{shop_id}'}
        response = requests.get(

            url=url,
            headers={'user-agent': f'{ua.random}'},
            cookies=cookies,
            verify=False
        )
        soup = BeautifulSoup(response.content, "html.parser")
        ul_list = soup.find("ul", {"class": "category-menu"})
        for li in ul_list.find_all("li", {"class": "category-menu__item"}):
            item = li.find("a", {"class": "category-menu__link"})
            name = item.get_text()
            if name not in ban_catalog:
                item_id = re.findall(r"/catalog/\d+/(\d+)", item.get("href"))[0]
                link = f"https://zakaz.atbmarket.com/catalog/{shop_id}/{item_id}?page="
                links.append({'name': name, 'link': link, 'shop_id': str(shop_id)})
        time.sleep(5)
    return links

