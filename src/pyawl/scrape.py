import decimal
import locale
import pprint
import re
from datetime import datetime

import requests
import time
from bs4 import BeautifulSoup
from decimal import Decimal


class Item(object):

    _itemName = re.compile('^itemName_(.*)')
    _itemPrice = re.compile('^itemPrice_(.*)')
    _monetary = locale.localeconv()

    def __init__(self, item):
        info = item.find('div', id=re.compile('^itemInfo_(.*)'), class_='a-fixed-right-grid-col g-item-details a-col-left')
        link = info.find('a', id=self._itemName)
        href = link['href']
        price = info.find('span', id=self._itemPrice).string.strip().replace('EUR ', '').replace(
            self._monetary['mon_thousands_sep'], '').replace(',', '.')
        try:
            price = Decimal(price)
        except decimal.InvalidOperation:
            price = Decimal(0)
        self.title = link['title'].strip()
        self.id = info['id'].replace('itemInfo_', '').strip()
        self.href = href.strip()
        self.price = Decimal(price)
        self.time = time.time()
        self.image = item.find('img')['src']
        self.date = datetime.now()

    def __repr__(self):
        return '{}\n{}\n{}\n{}'.format(self.title, self.price, self.href, self.time)


def parse(amazon_id='3F9MA6OUOXDV6', amazon_country='de', reveal='unpurchased', sortorder='date-added'):
    """
    :param amazon_id: wishlist id
    :param amazon_country: shop top level domain
    :param reveal: all, unpurchased or purchased
    :param sortorder: priority, universal-title, universal-price,
                        universal-price-desc, last-updated, date-added
    :return: list of Item
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    domain = 'http://www.amazon.{}/'.format(amazon_country)
    url = '{}/registry/wishlist/{}'.format(domain, amazon_id)
    response = requests.get(url, headers=headers, params={'reveal': reveal, 'sort': sortorder, 'layout': 'standard'})
    soup = BeautifulSoup(response.text, 'html.parser')
    list_div = soup.find_all('div', id=re.compile('^item_(.*)'), class_='a-fixed-left-grid a-spacing-large')
    #list_div = soup.find_all('div', id=re.compile('^itemInfo_(.*)'), class_='a-fixed-right-grid-col g-item-details a-col-left')
    return [Item(item) for item in list_div]

if __name__ == '__main__':
    for item in parse():
        pprint(item)