import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import datetime
import sqlite3
import requests
import os
import time


def add(fio, choice, today, flag=True):
    if choice in ['1', '2', '+']:
        cur.execute(f"""UPDATE List_pitanie
                SET {today} = '+'
                WHERE class = '{fio}'""").fetchall()
    else:
        cur.execute(f"""UPDATE List_pitanie
                SET {today} = '-'
                WHERE class = '{fio}'""").fetchall()
    con.commit()
    if flag:
        libr[fio] = choice
        write_msg(3, f'Ок.')


def write_msg(id, message):
    vk.method('messages.send', {
              'chat_id': id, 'message': message,
              'random_id': 0, 'keyboard': keyboard})


def get_name(user: int) -> str:
    data = vk.method("users.get", {"user_ids": user})[0]
    return "{} {}".format(data["last_name"], data["first_name"])


def get_keyboard(buttons):
    btns = []
    for i in range(len(buttons)):
        btns.append([])
        for j in range(len(buttons[i])):
            btns[i].append(None)
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            text = buttons[i][j][0]
            if buttons[i][j][1] == 'p':
                color = 'positive'
            if buttons[i][j][1] == 'n':
                color = 'negative'
            btns[i][j] = {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"" + "1" + "\"}",
                    "label": f"{text}"
                },
                "color": f"{color}"
            }
    my_keyboard = {
        'one_time': False,
        'buttons': btns
    }
    my_keyboard = json.dumps(my_keyboard, ensure_ascii=False).encode('utf-8')
    my_keyboard = str(my_keyboard.decode('utf-8'))
    return my_keyboard


os.environ["TZ"] = "Europe/Moscow"
time.tzset()
libr_clas = {'Цеденова Вика': 'Цеденова Виктория', 'Goryaev Naran': 'Горяев Наран',
             'Mandziev Aldar': 'Манджиев Алдар Д', 'Никутова Даяна': 'Оконова Даяна',
             'Штырин Дмитрий': 'Дживлеев Джангар', 'Виноградов Георгий': 'Манджиев Алдар Б',
             'Хулхачиева Саша': 'Хулхачиева Александра', 'Слыш Айса': 'Бурлинова Айса',
             'Убушаев Ростик': 'Убушаев Ростислав', 'Убушаева Александра': 'Манджиева Даяна',
             'Иванова Луиза': 'Гуспанова Анастасия'}
token = '6b7aec84bce00b4fa39982c89e52f51ed83fbd6e0a314d5c1f283a3a905d368133da9ba105494b1a01ad0'
vk = vk_api.VkApi(
    token=token)
longpoll = VkLongPoll(vk)
session_api = vk.get_api()
print('Server started')
keyboard = get_keyboard(
    [
        [('1', 'p')],
        [('2', 'p')],
        [('-', 'n')],
        [('заявка', 'p')]
    ]
)

t = datetime.datetime.now()
print(t)
libr = dict()
lst_days = ['first_d', 'second_d', 'third_d', 'fourth_d', 'fifth_d', 'sixth_d',
            'seventh_d', 'eighth_d', 'nineth_d', 'tenth_d', 'eleventh_d',
            'twelfth_d']
con = sqlite3.connect('list2.sqlite')
cur = con.cursor()
for day in lst_days:
    txt = f'''SELECT Class from List_pitanie WHERE {day} = "+"'''
    result = cur.execute(txt).fetchall()
    if not result:
        today = day
        break
write_msg(2, today)
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    if event.from_chat:
                        ti = datetime.datetime.now()
                        if ti.hour in range(7, 14) or\
                        get_name(event.user_id) == 'Зудаев Бадма':
                            txt = event.text
                            if 'CHANGE:' in txt.upper():
                                b1 = txt.split(':')
                                b = b1[1].split()
                                data = b.pop()
                                choice = b.pop()
                                fio = ' '.join(b)
                                add(fio, choice, data, False)
                            if 'CLEAN TABLE:' in txt.upper() and\
                                get_name(event.user_id) == 'Зудаев Бадма':
                                if txt.split()[2] == 'all':
                                    for day in lst_days:
                                        cur.execute(f"""UPDATE List_pitanie
                                            SET {day} = '-'""").fetchall()
                                        con.commit()
                                    today = lst_days[0]
                                else:
                                    cur.execute(f"""UPDATE List_pitanie
                                        SET {txt.split()[-1]} = '-'
                                        """).fetchall()
                                    con.commit()
                                write_msg(2, 'БД очищена.')
                            if txt in lst_days and\
                            get_name(event.user_id) == 'Зудаев Бадма':
                                libr = {}
                                today = txt
                                result = cur.execute(f"""SELECT class FROM List_pitanie
                                                    WHERE {today} LIKE '+'""").fetchall()
                                for i in result:
                                    libr[i[0]] = '+'
                                write_msg(2, 'День изменен.')
                                # доделать!!!
                            if txt.upper() == 'CLEAN' and\
                            get_name(event.user_id) == 'Зудаев Бадма':
                                libr = dict()
                                write_msg(2, 'Все очищено.')
                            if txt == f'[club202113221|@my_bot4] 1'\
                            or txt == f'[club202113221|@my_bot4] 2':
                                if get_name(event.user_id) in libr_clas:
                                    add(libr_clas[get_name(event.user_id)],
                                    txt[-1], today)
                                else:
                                    result = cur.execute(f"""SELECT Class
                                            FROM List_pitanie WHERE
                                            Class = '{get_name(
                                                event.user_id)}'""").fetchall()
                                    if result:
                                        add(result[0][0], txt[-1], today)
                                    else:
                                        write_msg(3,
                                                  "Такого ФИО нет в классе...")
                            if txt == f'[club202113221|@my_bot4] -':
                                if get_name(event.user_id) in libr_clas:
                                    add(libr_clas[get_name(event.user_id)],
                                        today, '-')
                                else:
                                    result = cur.execute(f"""SELECT Class
                                                FROM List_pitanie WHERE
                                                Class LIKE '%{get_name(
                                                event.user_id)}'""").fetchall()
                                    if result:
                                        add(result[0][0], '-', today)
                                    else:
                                        write_msg(3,
                                             "Такого ФИО нет в классе...")
                            if txt[:2] == '++' or txt[0] == '—' or\
                            txt[:2] == '--':
                                fio = list()
                                name, surname = txt.split()[2], txt.split()[1]
                                fio.append(surname)
                                fio.append(name)
                                if len(txt.split()) == 5 or txt.split()[0] in ['—', '--'] and len(txt.split()) == 4:
                                    dad = txt.split()[3]
                                    fio.append(dad)
                                fio = ' '.join(fio)
                                result = cur.execute(f"""SELECT class FROM List_pitanie
                                                    WHERE Class LIKE '%{fio}'""").fetchall()
                                if result:
                                    if '--' in txt or '—' in txt:
                                        add(fio, '-', today)
                                    else:
                                        if txt.split()[-1] in ('1', '2'):
                                            add(fio, txt.split()[-1], today)
                                        else:
                                            write_msg(3, 'Вы не ввели 1/2!')
                                else:
                                    write_msg(
                                        3, 'Вы ввели некорректное ФИО!')
                            if txt.upper() in ['PEOPLE'] or txt == f'[club202113221|@my_bot4] заявка':
                                one = [i for i in libr if libr[i] == '1']
                                two = [i for i in libr if libr[i] == '2']
                                plus = [i for i in libr if libr[i] == '+']
                                if txt == f'[club202113221|@my_bot4] заявка':
                                    write_msg(3, f'''Первое = {str(len(one))}
                                            Второе = {str(len(two))}''')
                                    application = str(
                                        ti.day) + '.' + str(ti.month)
                                    if one:
                                        one = sorted(one)
                                        application += '\nПервое:\n' + ', '.join(one)
                                    if two:
                                        two = sorted(two)
                                        application += '\nВторое:\n' + ', '.join(two)
                                    if plus:
                                        plus = sorted(plus)
                                        application += f'\nСписок: {len(plus)}\n' + ', '.join(plus)
                                    write_msg(3, application)
    except requests.exceptions.ReadTimeout:
        print("\n Переподключение к серверам ВК \n")
        time.sleep(3)
    except Exception as e:
        write_msg(2, 'Ошибка.')
        print(e)
