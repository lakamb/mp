import random
import pandas as pd
from datetime import datetime, timedelta
from wb_api import incomes, sales, stocks, orders


rnd = random.randint(90, 110)
sales['ttl_price'] = sales['finishedPrice'] * rnd


sales['date_column'] = pd.to_datetime(sales['date']).dt.date

def week_result():
    # Сколько рублей заработали за неделю?
    yesterday = max(sales['date_column'])
    week_ago = yesterday - timedelta(days=7)
    ttl_sum = int(sum(sales[(sales['date_column'] > week_ago)]['ttl_price']))

    return f'За прошедшую неделю прилетело ~{ttl_sum} рублей'

def bestseller():
    # Бестселлер
    grouppied = sales.groupby(['barcode']).agg({'ttl_price': ['sum']}).reset_index()
    grouppied.columns = ['barcode', 'ttl_sum']

    max_sells = max(grouppied['ttl_sum'])

    bestseller = grouppied[grouppied['ttl_sum'] == max_sells]['barcode']

    bestseller_desc = sales.merge(bestseller, on='barcode', how='inner')[['barcode', 'ttl_price', 'subject']].groupby(['barcode', 'subject']).agg({'ttl_price':['sum']}).reset_index()

    bestseller_desc.columns = ['barcode', 'subject', 'ttl_price']

    barcode = bestseller_desc['barcode'].values[0]
    subject = bestseller_desc['subject'].values[0]
    ttl_price = int(bestseller_desc['ttl_price'].values[0])

    return f'Лучше всех продавался товар с артикулом {barcode} категории "{subject}", который суммарно принес ~{ttl_price} рублей'
