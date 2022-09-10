import asyncio
import time
import datetime
from loguru import logger

from scrapers.atb import get_atb, get_categories_atb
from scrapers.silpo import get_silpo, get_categories_silpo

from db.schemas import ItemsShema
from db.models import Item, Items
from db.crud import SelectItem

from fake_useragent import UserAgent

ua = UserAgent()




async def scrap_supermarkets_loop():
    while True:
        try:
            logger.debug(f'Scraping...')
            bodies = get_categories_silpo()
            atb_links = get_categories_atb()

            silpo_items = []
            atb_items = []
            for atb_link in atb_links:
                    atb_items += get_atb(atb_link)
                    time.sleep(5)
            atb_items = ItemsShema(**{'items': atb_items})
            atb_items = Items(**{'items': check_duplicate(atb_items, 'atb')})
            for body in bodies:
                if body['name'] == 'Снеки':
                    silpo_items += get_silpo(body)
                    time.sleep(5)

            silpo_items = ItemsShema(**{'items': silpo_items})
            silpo_items = Items(**{'items': check_duplicate(silpo_items, 'silpo')})

            items = atb_items.items + silpo_items.items
            new, exist = check_existence(items)
            if new:
                SelectItem.create_all_items(Items(**{'items': new}))
            for e in exist:
                for s in e.shop_prices:
                    s['status'] = 0
                e.save()
            await asyncio.sleep(60 * 60 * 3)
        except Exception as e:
            logger.error(f'Не удалось получить информацию от супермаркетов: {e}')
            await asyncio.sleep(30)


async def main_loop():
    tasks = await asyncio.gather(
            scrap_supermarkets_loop(),
        return_exceptions=True
            )
    return tasks




def main():
    try:
        logger.info('Запуск бота')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_loop())
    except KeyboardInterrupt:
        logger.info('Good bye')


def check_existence(items):
    exist = SelectItem.select_all()
    new = []
    update = []
    for i in items:
        skip = True
        for e in exist:
            if i.title == e.title and i.shop == e.shop and i.shop_item_id == e.shop_item_id:
                e.price = i.price
                e.old_price = i.old_price
                e.shop_prices = i.shop_prices
                e.weight = i.weight
                e.history += i.history
                e.update_time = datetime.datetime.now()
                update.append(e)
                exist.remove(e)
                skip = False
                break
        if skip:
            new.append(i)
    SelectItem.update_items(update)
    return new, exist

def check_duplicate(items, market):
    new_list = []
    if market == 'silpo' or market == 'atb':
        for item in items.items:
            skip = False
            if len(new_list) == 0:
                new_list.append(
                    Item(title=item.title,
                         price=item.price,
                         old_price=item.old_price,
                         image=item.image,
                         link=item.link,
                         shop_item_id=item.shop_item_id,
                         weight=item.weight,
                         shop=market,
                         shop_prices=[{'shop': item.shop_id,
                                       'price': item.price}],
                         category=item.category,
                         history=item.history,
                         update_time=item.update_time,
                         ))
                continue
            for i in new_list:
                if item.shop_id not in [shop['shop'] for shop in i.shop_prices] \
                        and item.shop_item_id == i.shop_item_id:

                    i.shop_prices += [{'shop': item.shop_id,
                                       'price': item.price,
                                       'status': item.status}]
                    i.price = min([price['price'] for price in i.shop_prices])
                    skip = True
            if not skip:
                new_list.append(Item(title=item.title,
                                     price=item.price,
                                     old_price=item.old_price,
                                     image=item.image,
                                     link=item.link,
                                     shop_item_id=item.shop_item_id,
                                     weight=item.weight,
                                     shop=market,
                                     shop_prices=[{'shop': item.shop_id,
                                                   'price': item.price,
                                                  'status': item.status}],
                                     category=item.category,
                                     history=item.history,
                                     update_time=item.update_time,
                                     ))
    return new_list





if __name__ == '__main__':
    main()




