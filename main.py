# _*_ coding: utf-8 _*_
import gevent.monkey; gevent.monkey.patch_all()
import gevent.pool
import requests
import re
import json
import urlparse
from itertools import count
from shutil import copyfileobj
import urlparse
import os.path
import lxml
import lxml.html
from lxml.cssselect import CSSSelector
from lxml import etree
from gevent import Greenlet
from gevent.queue import Queue

# etree.tostring(root, pretty_print=True)
# etree.tostring(sel[0], encoding='unicode', pretty_print=True)

def pp(t):
	print etree.tostring(t, encoding='unicode', pretty_print=True)

queue = Queue(maxsize=300)
pool = gevent.pool.Pool(size=20)

galery_queue= Queue(maxsize=300)
galery_pool = gevent.pool.Pool(size=10)

index_template = 'http://www.chipmaker.ru/index.php?app=auction&sr={}'
lot_template = 'http://www.chipmaker.ru/index.php?app=auction&module=lot&lot={}'

# last =  480425
last = 471794

class Lot(object):
	pass


def parse_cats(tree):
	cats = []
	for x in tree.xpath('//a/@href'):
		params = dict((urlparse.parse_qsl(urlparse.urlparse(x).query)))
		maybe_cat = params.get('cat')
		if maybe_cat:
			cats.append(int(maybe_cat))
	return cats


def parse_location(tree):
	sel = CSSSelector(u'div.winSubHead ~ div:contains("Местонахождение")')(tree)
	string = etree.tostring(sel[0], encoding='unicode', pretty_print=True)
	date, place, views = re.findall(u'Дата публикации: (.+?)<br />.*?Местонахождение: (.+?)<br /.*?.*Просмотров: (.+?) <', string)[0]
	return date, place, views


def parse_price(tree):
	sel = CSSSelector(u'td:contains("Цена:")') # fix me. может быть цена в дескрипшене и отсос
	maybe_price_td = sel(tree)[-1]
	w = maybe_price_td.getnext()
	price = w.xpath('./div/div/text()')[0] # "1500 RUR"
	value, currency = re.findall('(\d+).(\w+)', price)[0]
	value = int(value)
	return value, currency


def parse_description(tree):
	pass
	# http://www.chipmaker.ru/index.php?app=auction&module=lot&lot=471796
	# import IPython; IPython.embed()

	# q = yoba.getparent().getparent()
	# string =  etree.tostring(q, encoding='unicode', pretty_print=True)

	# description = re.findall(u'</div>(.+?)</div>', string, re.MULTILINE | re.DOTALL)[-1]

	# print description

	# import IPython; IPython.embed()


def parse_lot(response, id_):
	# Тут парсим дерево в лот
	print id_
	tree = lxml.html.fromstring(response.text)
	if tree is not None:
		print 'no tree'
		return

	lot = Lot()
	lot.id = id_
	lot.title = tree.xpath('./head/title/text()')[0]
	
	# lot.price =
	# lot.cat_id = 

	category_ids = parse_cats(tree)
	price = parse_price(tree)

	# lot.country =
	# запросы
	# город
	# просмотры
	date, place, views = parse_location(tree)

	print lot.title, price, category_ids

	# lot.description =

	# description = parse_description(tree)


	# lot.vendor_id =  Информация о продавце
	# состояние =

	# запросы продавцу

	# import IPython; IPython.embed()

	# return lot


def main():
	# пока проходимся по сотне от последнего
	for lot_id in range(last, last+100):
		lot_url = lot_template.format(lot_id)
		lot_response = requests.get(lot_url)
		if lot_response.ok:
			# собственно обьект Lot уже можно куда-то сохранить
			print parse_lot(lot_response, lot_id)

if __name__ == "__main__":
    main()
