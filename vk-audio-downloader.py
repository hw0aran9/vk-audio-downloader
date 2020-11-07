#!/usr/bin/env python
# coding: utf-8

# TODO
# очистка имени файла только для win-систем
# decor time
# целевой каталог = название группы, если ничего не указано

import vk_api
from vk_api import audio
import requests
from time import time
import os


#данные для авторизации VK
LOGIN = ''     # Логин
PASSWORD = ''  # Пароль

# Путь к каталогу, в котором будет создана структура папок
PATH = r'D:\music'

# словарь с настройками
# внести туда пары ключ-значение вида
# ключ = id пользователя (положительное целое число) VK или группы (отрицательное)
# значение = название каталога внутри пути PATH, в который будет загружена музыка
PARAMS_DICT = {
 -1321027 : '_todd_edwards'
}


# очистка имени создаваемого файла от символов, которые не поддерживает Windows
def clean(s):
    bad_chars = ['/', '\\', ':', '*', '"', '?', '<', '>', '|']
    return ''.join(filter(lambda x: x not in bad_chars, s))

# основной метод установки сессии и загрузки трека в файл
def run_task(login, password, my_id, path, name_dir):
    path_to = path + name_dir
    if not os.path.exists(path_to):
        os.makedirs(path_to)

    print(f"Establishing session from {str(my_id)} -> {name_dir}")
    vk_session = vk_api.VkApi(login=login, password=password)
    vk_session.auth()
    vk_audio = audio.VkAudio(vk_session)
    print("Session established.")

    os.chdir(path_to)

    a = 0
    time_start = time()
    print("Retrieving tracks information...")

    tracks_info = vk_audio.get(owner_id=my_id)
    time_retrieving = time()

    print(f"Retrieved in {time_retrieving - time_start} seconds.")
    print(f"About {len(tracks_info)} tracks to download in current task.")

    for track in tracks_info:
        try:
            fetch_start_time = time()
            a += 1
            r = requests.get(track["url"])
            if r.status_code == 200:
                with open(clean(track["artist"]+'_'+track["title"])+'.mp3','wb') as output_file:
                    output_file.write(r.content)
            fetch_finish_time = time()
            total_time = fetch_finish_time - fetch_start_time
            print(f'[{a}/{len(tracks_info)}] FETCHED: '+track["artist"]+'_'+track["title"]+'.mp3'+f' in {total_time} sec.')

        except OSError:
            print('[ERROR] Failed to load track #' + str(a) + ' - ' + track["artist"] + '_' + track["title"])

    time_finish = time()
    print(f"Time elapsed: {time_finish - time_start} seconds.")

tasks = 0

print(f"Found {len(PARAMS_DICT)} task{'' if len(PARAMS_DICT) ==1 else 's'} for execution.")
for (key, value) in PARAMS_DICT.items():
    tasks += 1
    print(f"[TASK {tasks}] Started. Downloading from {'USER' if key >=0 else 'GROUP'}: {key} to - > //{value}.")
    try:
        run_task(LOGIN, PASSWORD, key, PATH, value)
        print(f"[TASK {tasks} SUCCESS] Download {key} -> {value} complete!")
    except:
        print(f'[TASK {tasks} FAILED!] {key} -> \\{value}')
