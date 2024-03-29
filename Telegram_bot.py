import requests
import json
from time import sleep
from Get_Music import *
from Get_Weather import temp

token = 'Please enter your telegram API token'
url = 'https://api.telegram.org/bot{}/'.format(token)


def getme():
    res = requests.get(url + "getme")
    d = res.json()
    username = d['result']['username']


def get_updates(offset=None):
    while True:
        try:
            URL = url + 'getUpdates'
            if offset:
                URL += '?offset={}'.format(offset)

            res = requests.get(URL)
            while (res.status_code != 200 or len(res.json()['result']) == 0):
                sleep(1)
                res = requests.get(URL)
            print(res.url)
            return res.json()

        except:
            pass


def get_last(data):
    results = data['result']
    count = len(results)
    last = count - 1
    last_update = results[last]
    return last_update


def get_last_id_text(updates):
    last_update = get_last(updates)
    chat_id = last_update['message']['chat']['id']
    update_id = last_update['update_id']
    try:
        text = last_update['message']['text']
    except:
        text = ''
    return chat_id, text, update_id


def ask_contact(chat_id):
    print('Ask Contact')
    text = 'Send Contact'
    keyboard = [[{"text": "Contact", "request_contact": True}]]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    send_message(chat_id, text, json.dumps(reply_markup))


def ask_location(chat_id):
    print('Ask Location')
    text = 'Please mark the location'
    keyboard = [[{"text": "Location Marker", "request_location": True}]]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    send_message(chat_id, text, json.dumps(reply_markup))


def get_location(update_id):
    print('Get Location')
    updates = get_updates(update_id + 1)
    location = get_last(updates)['message']['location']
    chat_id, text, update_id = get_last_id_text(updates)
    lat = str(location['latitude'])
    lon = str(location['longitude'])
    return lat, lon, update_id


def send_message(chat_id, text, reply_markup=None):
    URL = url + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        URL += '&reply_markup={}'.format(reply_markup)
    res = requests.get(URL)
    while res.status_code != 200:
        res = requests.get(URL)
    print(res.status_code)


def reply_markup_maker(data):
    keyboard = []
    for i in range(0, len(data), 2):
        key = []
        key.append(data[i].title())
        try:
            key.append(data[i + 1].title())
        except:
            pass
        keyboard.append(key)

    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def saavn(chat_id, update_id):
    message = 'Please select an option'
    commands = ['Hindi Chartbusters', 'English Chartbusters', 'Saavn Weekly Top']
    reply_markup = reply_markup_maker(commands)
    send_message(chat_id, message, reply_markup)
    chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))

    while text.lower() == 'saavn':
        chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))
        sleep(0.5)

    print(text)

    if text == 'Saavn Weekly Top':
        final_send = ''
        commands = ['English', 'Hindi']
        message = 'Please select a Language'
        reply_markup = reply_markup_maker(commands)
        send_message(chat_id, message, reply_markup)

        while text == 'Saavn Weekly Top':
            chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))
            sleep(0.5)

        print(text)

        lang = text.lower()
        songs = saavn_tops(lang)
        for i, item in enumerate(songs, 1):
            song = item.split('(')
            text = song[0]
            if len(song) == 2 and len(text + song[1]) < 30:
                text += '(' + song[1]

            final_send += str(i) + ". " + text + '\n\n'
        send_message(chat_id, final_send)


    elif text == 'Hindi Chartbusters':
        message = ''
        songs = hindi_chartbusters()
        for i, item in enumerate(songs, 1):
            song = item.split('(')
            text = song[0]
            if len(song) == 2 and len(text + song[1]) < 30:
                text += '(' + song[1]
            message += str(i) + ". " + text + '\n\n'
        send_message(chat_id, message)


    elif text == 'English Chartbusters':
        message = ''
        songs = english_chartbusters()
        for i, item in enumerate(songs, 1):
            song = item.split('(')
            text = song[0]
            if len(song) == 2 and len(text + song[1]) < 30:
                text += '(' + song[1]

            message += str(i) + ". " + text + '\n\n'
        send_message(chat_id, message)


def weather(chat_id, update_id):
    ask_location(chat_id)
    lat, lon, update_id = get_location(update_id)
    message = temp(lat, lon)
    send_message(chat_id, message)

def welcome_note(chat_id, commands):
    text = 'Please select an option'
    reply_markup = reply_markup_maker(commands)
    send_message(chat_id, text, reply_markup)


def start(chat_id):
    message = 'Hello there!! Let us get started :)'
    reply_markup = reply_markup_maker(['Start'])
    send_message(chat_id, message, reply_markup)

    chat_id, text, update_id = get_last_id_text(get_updates())
    while (text.lower() != 'start'):
        chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))
        sleep(0.5)

    return chat_id, text, update_id


def end(chat_id, text, update_id):
    message = 'Do you want to check anything else out?'
    reply_markup = reply_markup_maker(['Yes', 'No'])
    send_message(chat_id, message, reply_markup)

    new_text = text
    while (text == new_text):
        chat_id, new_text, update_id = get_last_id_text(get_updates(update_id + 1))
        sleep(1)

    if new_text == 'No':
        return 'y'
    else:
        return 'n'

def menu(chat_id, text, update_id):
    commands = ['weather', 'music']
    welcome_note(chat_id, commands)

    while (text.lower() == 'start'):
        chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))
        sleep(0.5)
    print(text)
    while text.lower() not in commands:
        chat_id, text, update_id = get_last_id_text(get_updates(update_id + 1))
        print(text)
        sleep(0.5)

    if text.lower() == 'music':
        saavn(chat_id, update_id)

    elif text.lower() == 'weather':
        weather(chat_id, update_id)

def main():
    text = ''
    chat_id, text, update_id = get_last_id_text(get_updates())
    chat_id, text, update_id = start(chat_id)
    print('Started')
    bye_message='Okayy!! See you soon :)'

    while text.lower() != 'y':
        sleep(1)
        text = 'Option bar'
        menu(chat_id, text, update_id)
        text = 'y'
        chat_id, text, update_id = get_last_id_text(get_updates())
        text = end(chat_id, text, update_id)
    if text.lower() == 'y':
        send_message(chat_id,bye_message)

if __name__ == '__main__':
    main()