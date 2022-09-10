from config import TelegramToken, logger, SILPOshops, ATBshops
from db.crud import SelectItem
from methods import restricted, search_item

import datetime
from telegram import (

    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,

    ConversationHandler,
    MessageHandler,
    Filters
)
from telegram.ext.defaults import Defaults

TYPED_ITEM, NUMBER = range(2)





@restricted
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/find - поиск товара\n/cancel - отмена поиска')

@restricted
def help_handler(update: Update, context: CallbackContext) -> None:

    update.message.reply_text('/find - поиск товара\n/cancel - отмена поиска')
@restricted
def find_handler(update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            text="Введите название товара:",
        )
        return TYPED_ITEM







@restricted
def item_handler(update: Update, context: CallbackContext):
    items = SelectItem.select_all()
    items = search_item(items, update.message.text)
    MSG = ''
    counter = 1
    save_items = []
    for i in items:
        weight = ''
        if i.weight:
            weight = f" {i.weight}"
        MSG += f"{counter}) {i.title}{weight} ({i.price} грн, {i.shop})\n"
        # context.user_data[TYPED_ITEM] = update.message.text
        save_items.append({'my_id': counter, 'item': i})
        counter += 1

    if not items:
        MSG = 'Ничего не найдено. Введите название снова или отмените поиск /cancel'
        update.message.reply_text(
            MSG,
        )
        return TYPED_ITEM

    else:
        context.user_data['Items'] = save_items
        MSG += "\nЧтобы получить подробную информацию, напишите номер товара: "
    if len(MSG) > 4096:
        for x in range(0, len(MSG), 4096):
            update.message.reply_text(MSG[x:x + 4096])
    else:
        update.message.reply_text(MSG)

    return NUMBER

@restricted
def item_info_handler(update: Update, context: CallbackContext):
    number = check_number(update.message.text, context.user_data["Items"])
    if not number:
        # update.message.reply_text('Пожалуйста, введите корректный номер.')
        item_handler(update, context)
        return NUMBER
    context.user_data[NUMBER] = number

    for item in context.user_data["Items"]:
        if item['my_id'] == context.user_data[NUMBER]:
            price_history = ""
            history = item['item'].history
            history.reverse()
            prev_date = None
            for h in history:
                date = datetime.datetime.strptime(h['Date'], ('%Y-%m-%dT%H:%M:%S.%f'))
                if prev_date:
                    if prev_date.date() == date.date():
                        continue
                    else:
                        prev_date = date
                else:
                    prev_date = date
                price_history += f"    {date.strftime('%d/%m/%Y')} - {h['Price']} грн\n"
            weight = ''
            if item['item'].weight:
                weight = f"({item['item'].weight})"
            shops = ''
            for shop in item['item'].shop_prices:
                if shop['status'] == 1:
                    if item['item'].shop == 'silpo':
                        shops += f"    {SILPOshops[shop['shop']]} | {shop['price']}\n"
                    if item['item'].shop == 'atb':
                        shops += f"    {ATBshops[shop['shop']]} | {shop['price']}\n"
            text = f"""• Название: {item['item'].title} {weight}
• Цена: {item['item'].price} грн
• Магазин: {item['item'].shop}\n{shops}
• Ссылка: {item['item'].link}
• История цен:\n{price_history}
            """

            try:
                update.message.reply_photo(photo=item['item'].image, caption=text)
            except:
                update.message.reply_text(text)
            break
    return ConversationHandler.END


@restricted
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Отмена. Для нового поиска введите /find')
    return ConversationHandler.END

def check_number(number,items):
    try:
        number = int(number)
    except (TypeError, ValueError):
        return None

    if number < 0 or number > len(items):
        return None
    return number

def telegram_main() -> None:
    updater = Updater(TelegramToken,
                      defaults=Defaults(run_async=True),)


    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('find', find_handler)],
        states={
            TYPED_ITEM: [
                MessageHandler(Filters.text & (~ Filters.command), item_handler, pass_user_data=True),
            ],
            NUMBER: [
                MessageHandler(Filters.text & (~ Filters.command), item_info_handler, pass_user_data=True),
            ],

        },
        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('find', find_handler)
                   ],
    )
    dispatcher.add_handler(conv_handler)


    updater.start_polling()

if __name__ == '__main__':
    telegram_main()