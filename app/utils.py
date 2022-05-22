import os
from typing import List
from decimal import Decimal
import xml.etree.ElementTree as ET

import requests
import gspread


telegram_token = os.environ.get('TELEGRAM_TOKEN')
user_id = os.environ.get('TELEGRAM_USER_ID')


def get_quotes() -> Decimal:
    """Функция получения курса $"""
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed [get_quotes]', e)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        value = root.find(".//*[@ID='R01235']/Value")
        return Decimal(value.text.replace(',', '.'))


def get_google_sheet(sheet_name: str) -> List[list]:
    """Функция загрузки таблицы из google sheets"""
    client = gspread.service_account('key.json', gspread.auth.READONLY_SCOPES)
    spreadsheet = client.open(sheet_name)
    value = spreadsheet.sheet1.get()
    return value


def send_message_to_telegram(order: str) -> bool:
    text = f"Заказ №{order} не доставлен"
    try:
        response = requests.get(
            url=f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            params={"chat_id": user_id, "text": text},
            headers={"Content-Type": "application/octet-stream"}
        )
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed [send_message_to_telegram]', e)
        return False
