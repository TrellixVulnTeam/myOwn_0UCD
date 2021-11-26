import datetime
from datetime import datetime
import shelve

import files


async def log(text):
    time = str(datetime.now())
    try:
        with open(files.working_log, 'a', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')
    except:
        with open(files.working_log, 'w', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')


def get_admin_list():
    admins_list = []
    with open(files.admins_list, encoding='utf-8') as f:
        for admin_id in f.readlines():
            admins_list.append(int(admin_id))
    return admins_list


def get_moder_list():
    moders_list = []
    with open(files.moders_list, encoding='utf-8') as f:
        for moder_id in f.readlines():
            moders_list.append(int(moder_id))
    return moders_list


def new_admin(his_id):
    with open(files.admins_list, encoding='utf-8') as f:
        if not str(his_id) in f.read():
            with open(files.admins_list, 'a', encoding='utf-8') as f: f.write(str(his_id) + '\n')


def new_moder(his_id):
    with open(files.moders_list, encoding='utf-8') as f:
        if not str(his_id) in f.read():
            with open(files.moders_list, 'a', encoding='utf-8') as f: f.write(str(his_id) + '\n')


def get_state(chat_id):
    with shelve.open(files.state_bd) as bd:
        if str(chat_id) in bd: return True


def user_logger(chat_id):
    if chat_id == 0:
        users_list = []
        with open(files.users_list, encoding='utf-8') as f:
            for user_id in f.readlines():
                users_list.append(int(user_id))
        return users_list
    else:
        if chat_id not in get_admin_list():
            with open(files.users_list, encoding='utf-8') as f:
                if not str(chat_id) in f.read():
                    with open(files.users_list, 'a', encoding='utf-8') as f: f.write(str(chat_id) + '\n')


def new_blocked_user(his_id):
    with open(files.blockusers_list, 'w', encoding='utf-8') as f: return f.write(str(his_id) + '\n')


def check_message(message):
    with shelve.open(files.bot_message_bd) as bd:
        if message in bd:
            return True
        else:
            return False


def del_id(file, chat_id):
    text = ''
    with open(file, encoding='utf-8') as f:
        for i in f.readlines():
            i = i[:len(i) - 1]
            if str(chat_id) == i:
                pass
            else:
                text += i + '\n'
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)
