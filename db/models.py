import datetime
import json
from playhouse.sqlite_ext import Model, CharField, FloatField, TextField, DateTimeField, IntegerField
from typing import List
from db.database import db


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value, default=default)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class BaseModel(Model):
    class Meta:
        database = db


class Item(BaseModel):

    title = CharField()
    price = FloatField()
    old_price = FloatField(null=True)
    image = CharField()
    link = CharField()
    shop = CharField()
    category = CharField()
    shop_prices = JSONField()
    shop_item_id = IntegerField()
    history = JSONField()
    weight = CharField(null=True)
    update_time = DateTimeField(default=datetime.datetime.now())
    # status = IntegerField(default=0)


    # avg_price = FloatField(null=True)
    # weight = CharField(null=True)








    # status = IntegerField(default=0)

    class Meta:
        indexes = (
            (('title', 'shop', 'link'), True),

        )


class Items(BaseModel):
    items: List[Item]

