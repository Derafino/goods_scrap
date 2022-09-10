

from db.models import Item, db



db.connect()
Item.create_table()
Item.create_table()
db.close()



class SelectItem:
    @staticmethod
    def create_all_items(items):
        with db.atomic():
            Item.bulk_create(items.items, batch_size=500)

    @staticmethod
    def select_all():
        items = Item.select()
        return [item for item in items]

    @staticmethod
    def update_items(items):
        with db.atomic():
            Item.bulk_update(items, fields=[Item.price,
                                            Item.old_price,
                                            Item.shop_prices,
                                            Item.history,
                                            Item.weight,
                                            Item.update_time], batch_size=50)








