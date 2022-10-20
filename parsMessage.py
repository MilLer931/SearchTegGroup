from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.messages import ReadHistoryRequest
from telethon.tl.types import InputPeerEmpty
import os
import sys
import configparser
import csv
import time
import json

RE = "\033[1;31m"
GR = "\033[1;32m"
CY = "\033[1;36m"


def banner():
    print(f"""
´´´´¶¶¶¶¶¶´´´´´´¶¶¶¶¶¶
´´¶¶¶¶¶¶¶¶¶¶´´¶¶¶¶¶¶¶¶¶¶
´¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶´´´´¶¶¶¶
¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶´´´´¶¶¶¶
¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶´´¶¶¶¶¶
¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶ ´¶¶¶¶¶´
´´¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶
´´´´´¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶
´´´´´´´¶¶¶¶¶¶¶¶¶¶¶¶¶
´´´´´´´´´¶¶¶¶¶¶¶¶
´´´´´´´´´´´¶¶¶¶
{RE}

by vimikh
        """)


if __name__ == "__main__":
    cpass = configparser.RawConfigParser()
    cpass.read('config.data')

    try:
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        client = TelegramClient(phone, api_id, api_hash)
    except KeyError:
        os.system('clear')
        banner()
        print(RE + "[!] run python3 setup.py first !!\n")
        sys.exit(1)

    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        os.system('clear')
        banner()
        client.sign_in(phone, input(GR + '[+] Enter the code: ' + RE))

    os.system('clear')
    banner()
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        groups.append(chat)

    print(GR + '[+] Choose a group to scrape members :' + RE)
    i = 0
    for g in groups:
        print(GR + '[' + CY + str(i) + GR + ']' + CY + ' - ' + g.title)
        i += 1

    print()
    g_index = input(GR + "[+] Enter a Number : " + RE)
    target_group = groups[int(g_index)]

    len_chat = client.get_messages(target_group).total
    print("Count of messages in a group: " + str(len_chat))
    all_words = input(GR + "[+] Enter a Words for search: " + RE).lower()
    words_list = all_words.split()

    input_limit = input(
        GR + '[' + CY + '+' + GR + ']' + CY + ' do you want to enable limit search messages(y/n): ').lower()
    if input_limit == "y":
        try:
            state_limit = int(input(GR + '[' + CY + '+' + GR + ']' + CY + ' Enter a limit: '))
        except AttributeError:
            print(GR + '[' + RE + 'Error' + GR + ']' + RE + ' Limit entered error. Start without limit.')
            state_limit = len_chat
    else:
        state_limit = len_chat
    print(GR + '[+] Fetching Words...')
    messages = client.get_messages(target_group, limit=state_limit)
    messages_list = []
    for message in messages:
        try:
            if set(words_list).issubset(set(message.text.lower().split())):
                participant = client.get_participants(message.from_id.user_id)[0]
                messages_list.append({
                    "first_name": participant.first_name if participant.first_name else "",
                    "last_name": participant.last_name if participant.last_name else "",
                    "message": message.text
                })
        except AttributeError:
            continue
    with open("messages.json", "w", encoding='utf8') as f:
        json.dump(messages_list, f, ensure_ascii=False)
    print(GR + '[+] Words fetched successfully.')
