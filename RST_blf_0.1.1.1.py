import telebot
from telebot import types
from config import TOKEN
import pymysql.cursors
import requests
import time
bot = telebot.TeleBot(TOKEN)
con = pymysql.connect(host='localhost', user='root', password='root', db='rst_db')
Headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.111 Safari/537.36'
}
kb = types.ReplyKeyboardMarkup()
kb.row('/start', '/sign')
kb.row('/remove', '/unsign')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'ТЕСТОВЫЙ РЕЖИМ!!!\n'
                                      'Я буду отправлять вам уведомлеия о новых авто в продаже на\n сайте RST, '
                                      'для продолжения работы нажмите кнопку: \n \n'
                                      '/sign - и вставьте скопированую строку поиска с сайта RST.\n'
                                      '/remove - для удаления всех ваших запросов из БД\n'
                                      '/unsign - для удаления вашей записи и прекращения работы', reply_markup=kb)
    print(message.from_user.last_name)
    print(type(message))


@bot.message_handler(commands=['sign'])
def start_message(message):
    try:
        add_new_client(message.chat.id)
        bot.send_message(message.chat.id, 'Я записал вас в свою базу')
        logging(message.chat.id, 'The client is ADDED to the base')
    except pymysql.err.IntegrityError:
        bot.send_message(message.chat.id, 'Вы уже пользуетесь нашей услугой ')
        logging(message.chat.id, 'The client has ALREADY been added to the database')


@bot.message_handler(commands=['remove'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я удалил ваш запрос')
    del_urls(message.chat.id)
    del_cars(message.chat.id)
    logging(message.chat.id, 'Clients requests deleted')


@bot.message_handler(commands=['unsign'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я удалил вас из базы, до встречи!')
    remove_client(message.chat.id)
    logging(message.chat.id, 'Client Removed')


@bot.message_handler(content_types=['text'])
def catch_url(message):
    url = message.text
    try:
        if str(requests.get(url, headers=Headers, verify=False, allow_redirects=True)) != '<Response [200]>':
            bot.send_message(message.chat.id, 'Нерабочая ссылка')
        elif url in get_urls(message.chat.id):
            bot.send_message(message.chat.id, 'Этот запрос уже добавлен вами в базу')
        else:
            add_url(message.chat.id, url)
            bot.send_message(message.chat.id, 'Ссылка добавлена')
            logging(message.chat.id, 'Added new client REQUESTS')
    except requests.exceptions.ConnectionError:
        bot.send_message(message.chat.id, 'Проверьте правильность ссылки, пожалуйста')
    except requests.exceptions.MissingSchema:
        bot.send_message(message.chat.id, 'Проверьте правильность ссылки, пожалуйста')


def add_new_client(id):
    con.connect()
    try:
        with con.cursor() as cursor:
            query = 'INSERT INTO clients_id (id) VALUES(%s)'
            cursor.execute(query, (id))
        con.commit()
    finally:
        con.close()


def remove_client(id):
    del_urls(id)
    del_cars(id)
    con.connect()
    try:
        with con.cursor() as cursor:
            query = 'DELETE FROM clients_id WHERE id = %s'
            val = id
            cursor.execute(query, val)
        con.commit()
    finally:
        con.close()


def add_url(id, urls):
    con.connect()
    try:
        with con.cursor() as cursor:
            query = 'INSERT INTO urls VALUES (%s, %s)'
            val = (id, urls)
            cursor.execute(query, val)
        con.commit()
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


def del_urls(ids):
    con.connect()
    try:
        with con.cursor() as cursor:
            sql = "DELETE FROM urls WHERE id= %s"
            val = ids
            cursor.execute(sql, val)
        con.commit()
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


def del_cars(ids):
    con.connect()
    try:
        with con.cursor() as cursor:
            sql = "DELETE FROM cars WHERE id= %s"
            val = ids
            cursor.execute(sql, val)
        con.commit()
    finally:
        con.close()


def logging(id=None, log_message=None):
    log = open('log_listener.txt', 'a')
    log.write(time.asctime() + '\t' + 'id = ' + str(id) + ' ' + str(log_message) + '\n')
    log.close()


bot.polling()
