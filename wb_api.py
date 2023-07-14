import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import random
from datetime import datetime, timedelta
from config import wb_TOKEN

TOKEN = wb_TOKEN

url = "https://statistics-api-sandbox.wildberries.ru/api/v1/supplier/sales?dateFrom=2022-01-01" #продажи

headers = CaseInsensitiveDict()
headers["Authorization"] = TOKEN


resp = requests.get(url, headers=headers)

df = pd.DataFrame(resp.json())

rnd = random.randint(90, 110)
df['ttl_price'] = df['finishedPrice'] * rnd


df['date_column'] = pd.to_datetime(df['date']).dt.date

def week_result():
    # Сколько рублей заработали за неделю?
    yesterday = max(df['date_column'])
    week_ago = yesterday - timedelta(days=7)
    ttl_sum = int(sum(df[(df['date_column'] > week_ago)]['ttl_price']))

    return f'За прошедшую неделю прилетело ~{ttl_sum} рублей'

def bestseller():
    # Бестселлер
    grouppied = df.groupby(['barcode']).agg({'ttl_price': ['sum']}).reset_index()
    grouppied.columns = ['barcode', 'ttl_sum']

    max_sells = max(grouppied['ttl_sum'])

    bestseller = grouppied[grouppied['ttl_sum'] == max_sells]['barcode']

    bestseller_desc = df.merge(bestseller, on='barcode', how='inner')[['barcode', 'ttl_price', 'subject']].groupby(['barcode', 'subject']).agg({'ttl_price':['sum']}).reset_index()

    bestseller_desc.columns = ['barcode', 'subject', 'ttl_price']

    barcode = bestseller_desc['barcode'].values[0]
    subject = bestseller_desc['subject'].values[0]
    ttl_price = int(bestseller_desc['ttl_price'].values[0])

    return f'Лучше всех продавался товар с артикулом {barcode} категории "{subject}", который суммарно принес ~{ttl_price} рублей'
