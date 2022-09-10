from config import Chats
from functools import wraps
from fuzzywuzzy import process


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in Chats:
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def search_item(items, search_query):
    searched = process.extract(search_query, [i.title for i in items], limit=30)
    searched = [s[0] for s in searched]
    find_search = []
    for s in searched:
        for i in items:
            if i.title == s:
                find_search.append(i)
                break
    return find_search
