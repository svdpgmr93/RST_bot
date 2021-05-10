import telebot
import requests
import pymysql.cursors
import time
from bs4 import BeautifulSoup
from config import TOKEN
bot = telebot.TeleBot(TOKEN)
HOST = 'https://rst.ua'
Headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.111 Safari/537.36'
}
con = pymysql.connect(host='localhost', user='root', password='root', db='rst_db')


def send_car(id, data):
    bot.send_message(id, data)


def get_soup(url):
    links = []
    ids = []
    html = BeautifulSoup(requests.get(url, headers=Headers, verify=False, allow_redirects=True).text, 'html.parser')
    div = html.find_all('a', class_='rst-ocb-i-a')
    for car in div:
        links.append(car.get('href'))
    for elem in links:
        ids.append(HOST + elem)
    return ids


def get_ids():
    con.connect()
    try:
        with con.cursor() as cursor:
            sql = "SELECT * FROM clients_id"
            cursor.execute(sql)
            result = cursor.fetchall()
            out_mass = []
            for elem in result:
                out_mass.append(elem[0])
            return out_mass
    finally:
        con.close()


def get_urls(ids):
    con.connect()
    try:
        with con.cursor() as cursor:
            sql = "SELECT urls FROM urls WHERE id= %s"
            val = ids
            cursor.execute(sql, val)
            result = cursor.fetchall()
            out_mass = []
            for elem in result:
                out_mass.append(elem[0])
            return out_mass
    finally:
        con.close()


def get_cars(ids):
    con.connect()
    try:
        with con.cursor() as cursor:
            sql = "SELECT cars FROM cars WHERE id= %s"
            val = ids
            cursor.execute(sql, val)
            result = cursor.fetchall()
            out_mass = []
            for elem in result:
                out_mass.append(elem[0])
            return out_mass
    finally:
        con.close()


def add_cars(id, cars):
    con.connect()
    try:
        with con.cursor() as cursor:
            query = 'INSERT INTO cars VALUES (%s, %s)'
            val = (id, cars)
            cursor.execute(query, val)
        con.commit()
    finally:
        con.close()


def main_func():
    for id in get_ids():
        in_cars_mass = []
        for url in get_urls(id):
            in_cars_mass += get_soup(url)
        if get_cars(id) != []:
            for elem in in_cars_mass:
                if elem not in get_cars(id):
                    add_cars(id, elem)
                    send_car(id, elem)
                    logging(id, elem)
        else:
            for elem in in_cars_mass:
                add_cars(id, elem)


def logging(id=None, log_message=None):
    log = open('log_sender.txt', 'a')
    log.write(time.asctime() + '\t' + 'id = ' + str(id) + ' send car ' + str(log_message) + '\n')
    log.close()


i = 1
while True:
    print(i)
    main_func()
    i += 1
    time.sleep(600)
