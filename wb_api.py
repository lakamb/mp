import requests
from requests.structures import CaseInsensitiveDict
from config import wb_TOKEN
import pandas as pd

TOKEN = wb_TOKEN

headers = CaseInsensitiveDict()
headers["Authorization"] = TOKEN


init = 'https://statistics-api-sandbox.wildberries.ru/api/v1/supplier/'
dateFrom = '2022-01-01'
results = {i: f'{init}{i}?dateFrom={dateFrom}' for i in ['incomes', 'sales', 'stocks', 'orders']}

incomes = pd.DataFrame(requests.get(results['incomes'], headers=headers).json()) #поставки
sales = pd.DataFrame(requests.get(results['sales'], headers=headers).json()) #продажи
stocks = pd.DataFrame(requests.get(results['stocks'], headers=headers).json()) #остатки
orders = pd.DataFrame(requests.get(results['orders'], headers=headers).json()) #заказы
