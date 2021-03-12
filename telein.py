from telebot import types, TeleBot
from database import UseDB as db
from secret import TOKEN

bot = TeleBot(TOKEN)


def make_good(table):
    message = 'Статус ус-в:\n'
    for numb, row in zip(range(10), table):
        formated_status = {1: '✅',
                           2: '🛑 (disabled)',
                           0: '❌',
                           -1: '❔'}[row[5]]
        name = row[1]
        ip = row[2]
        message += f'{formated_status} {name} - {ip}\n'

    return message


@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['status'])
def status_hadler(message):
    table = db().get_all()
    msg = make_good(table)

    markup = types.InlineKeyboardMarkup()
    update_button = types.InlineKeyboardButton('u', callback_data="ref")
    next_button = types.InlineKeyboardButton('->', callback_data="p-1")

    markup.add(update_button, next_button)

    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(commands=['add'])
def add_device(message):
    msg = bot.send_message(message.chat.id, 'Введите имя, адрес и тип ус-ва, например Switch-48 192.168.1.1 ap')
    bot.register_next_step_handler(msg, add_dev_fin)


def add_dev_fin(message):
    name, ip, dev_type = message.text.split()
    db().add_device(name, ip, dev_type)
    bot.send_message(message.chat.id, 'Успешно!')


@bot.callback_query_handler(func=lambda call: 'p' in call.data.split('-')[0])
def next_page_handler(call):
    table = db().get_all()
    msg = make_good(table[int(call.data.split('-')[1])*10:])

    prv_d = 'p-{}'.format(int(call.data.split('-')[1])-1)
    nxt_d = 'p-{}'.format(int(call.data.split('-')[1])+1)

    markup = types.InlineKeyboardMarkup()

    prv_btn = types.InlineKeyboardButton('<-', callback_data=prv_d)
    nxt_btn = types.InlineKeyboardButton('->', callback_data=nxt_d)

    k = len(table)//10 + (1 if len(table) % 10 != 0 else 0) - 1
    p = int(call.data.split('-')[1])

    if p > 0 and p < k:
        markup.add(prv_btn, nxt_btn)
    elif p == 0 and p < k:
        markup.add(nxt_btn)
    elif p > 0 and p >= k:
        markup.add(prv_btn)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=msg,
                          reply_markup=markup)


if __name__ == "__main__":
    bot.polling()
