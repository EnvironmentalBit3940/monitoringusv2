from database import UseDB as db
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import popen, system
import telebot
import logging

# Настройка лога
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('monitoring.log')
handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# Настройка бота
TOKEN = '1481680706:AAFQw626tswo2Y2jF0JE48gltIymuCBlAIE'
bot = telebot.TeleBot(TOKEN)
chat_id = '-315456175' # ''64634999
bot.send_message(chat_id, 'Я работаю тут!')

# TODO: ups_mon, сообщения для телеги
# Объявление асинхронных функций
def check_status(host):
    name, dev_type, old_status, msg = db().get_device(host)
    # Для AP
    status = int(old_status)
    logger.info('Проверяю %s...', name)
    if dev_type == 1:
        resp = system(f'ping -c 3 -W 2 {host} > /dev/null')
        # Если не ответил и статус не нулевой
        if resp != 0 and status != 0:
            status = 0
            db().update_status(host, status)
            logger.warning('%s упал', name)
            bot.send_message(chat_id, f'{name if name else host} упал, поднимите')
        # Если хоть раз не ответил, но сейчас норм
        elif resp == 0 and status != 1:
            status = 1
            db().update_status(host, status)
            logger.warning('%s поднялся', name)
            bot.send_message(chat_id, f'{name if name else host} поднялся!')
    # Для PC
    elif dev_type == 2:
        resp_nbt = popen(f'nbtscan -t 1000 {host} | grep {host}').read().split('\n')[1]
        # Не пришло ответа
        logger.debug('%s, resp_nbt: %s', name, resp_nbt)
        if resp_nbt == '':
            resp_nmap = popen(f'nmap -O {host} | grep MAC').read()
            logger.debug('%s, resp_nmap: %s', name, resp_nmap)
            if 'MAC' not in resp_nmap and status != 0:
                status = 0
                db().update_status(host, status)
                logger.warning('%s упал', name)
                bot.send_message(chat_id, f'{name if name else host} упал, поднимите')
            elif 'MAC' in resp_nmap and status !=1:
                status = 1
                db().update_status(host, status)
                logger.warning('%s поднялся', name)
                bot.send_message(chat_id, f'{name if name else host} поднялся!')
        # Пришел ответ, а до этого был мертвым
        elif resp_nbt != '' and status != 1:
            status = 1
            db().update_status(host, status)
            logger.info('%s поднялся', name)
            bot.send_message(chat_id, f'{name if name else host} поднялся!')

    return host, status, {True: "changed", False: "stay"}[old_status != status]


while True:
    dev_list = db().get_all()
    results, ips_list = [], []
    [ips_list.append(row[2]) for row in dev_list]
    with ThreadPoolExecutor() as execut:
        results.append(execut.map(check_status, ips_list))

