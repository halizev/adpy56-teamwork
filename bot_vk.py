from random import randrange

import dating_db
from dating_db import DatingDB
import configparser
import requests
import vk_api
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    user = config["db_info"]["user"]
    password = config["db_info"]["password"]
    name_db = config["db_info"]["database"]
    token_group = config["vk_info"]["token_group"]
    token_user = config["vk_info"]["token_user"]

    vk = vk_api.VkApi(token=token_group)
    longpoll = VkLongPoll(vk)
    db = DatingDB(name_db, user, password)
    db.connect_db()

    def write_msg(user_id, message):
        vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

    def get_user_info(user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': token_group,
                  'user_ids': user_id,
                  'fields': 'name, sex, city, bdate',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_dict = response['response']
            for info in information_dict:
                user_first_name = info['first_name']
                user_last_name = info['last_name']
                user_sex = info['sex']
                user_city_id = info['city']['id']
                user_bdate = datetime.strptime(info['bdate'], "%d.%m.%Y")

                return [user_id, user_first_name, user_last_name, user_bdate, user_sex, user_city_id]
        except KeyError:
            write_msg(user_id, 'Ошибка получения токена, введите токен в переменную - user_token')

    def search_user_candidates(user_id):
        url = f'https://api.vk.com/method/users.search'
        user_info_array = dating_db.get_user_info(user_id)

        user_sex = 0
        if user_info_array[0] == 1:
            user_sex = 2
        elif user_info_array[0] == 2:
            user_sex = 1

        birthday = user_info_array[0].date()
        today = datetime.date.today()
        user_age = today.year - birthday.year
        if (today.month < birthday.month or
                (today.month == birthday.month and today.day < birthday.day)):
            user_age = user_age - 1

        params = {'access_token': token_user,
                  'v': '5.131',
                  'sex': user_sex,
                  'age': user_age,
                  'city': user_info_array[2],
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': '1' or '6',
                  'has_photo': '1',
                  'count': 100}
        repl = requests.get(url, params=params)
        response = repl.json()

        try:
            candidates_info = response['items']
            for person_dict in candidates_info:
                if person_dict['is_closed'] == False:
                    candidate_first_name = person_dict['first_name']
                    candidate_last_name = person_dict['last_name']
                    candidate_id = str(person_dict['id'])
                    candidate_link = 'vk.com/id' + str(person_dict['id'])
                    dating_db.add_candidate(candidate_id, candidate_first_name, candidate_last_name, candidate_link)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            write_msg(user_id, 'Ошибка получения токена')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_request = str(event.text.lower())
                user_id = str(event.user_id)

                if user_request == "начать":
                    write_msg(event.user_id, f"Хай, {user_id}")
                    get_user_info(user_id)
                    if not db.check_user_id(event.user_id):
                        # тут будет функция получения из вк информации(возраст, пол, город) о пользователе для записи в бд 
                        db.add_user(event.user_id, 'Люда', 40, 'female', 'Kaluga')                
                elif user_request == "поиск":
                    write_msg(event.user_id, f"Начинаю поиск для {event.user_id}")

                    # тут функция поиска кадидатов(передаём инфо о пользователе из бд,
                    search_user_candidates(user_id)
                    # получаем файл json(имя, фамилия, ссылка на профиль, три ссылки на фото))
                    # Здесь будет вывод пользователей
                    # до написания функции временно набросаю список:
                    user_candidate_list = [
                        {'user_id':2089706, 'candidate_id':3, 'name':'Jon', 'surname':'Bidon', 'profile_link':'pr_link1', 'attachments':['photo1','photo2','photo3'], 'favourite':False, 'has_seen':False},
                    {'user_id':2089706, 'candidate_id':4, 'name':'Ion', 'surname':'Suruchianu', 'profile_link':'pr_link2', 'attachments':['photo1','photo2','photo3'], 'favourite':False, 'has_seen':False},
                    {'user_id':2089706, 'candidate_id':5, 'name':'Sofia', 'surname':'Rotaru', 'profile_link':'pr_link3', 'attachments':['photo1','photo2','photo3'], 'favourite':False, 'has_seen':False}
                    ]
                    # если в базе нет кадидата, то создаём запись
                    for candidate in user_candidate_list:
                        if not db.check_candidate_id(candidate['candidate_id']): 
                            db.add_candidate(candidate['candidate_id'], candidate['name'], candidate['surname'], candidate['profile_link'])
                            db.add_photo(candidate['candidate_id'], candidate['attachments']) # после готового кода взаимодействия с вк тут будут данные из json
                        if not db.check_user_vk_candidate_id(event.user_id, candidate['candidate_id']):
                            db.add_user_vk_candidate(candidate['user_id'], candidate['candidate_id'], candidate['favourite'], candidate['has_seen']) # после готового кода взаимодействия с вк тут будут данные из json
                    # сохраняем данные о кандидатах в список для отображения пользователю
                    candidates_list = db.get_candidates(event.user_id)
                    # тут будет функция write_msg("следующий", "в избранное"), 
                    # которая отображает пользователю данные о подходящих
                    # кандидатах по одному, на интерфейсе в чате с ботом будут кнопки
                    # "следующий", "в избранное"
                # после нажатия на кнопку вперёд помечаем флаг has_seen
                elif user_request == "следующий": # переделать механизм на кнопку
                    write_msg(event.user_id, "Предыдущий промаркирован has_seen") 
                    db.mark_has_seen(event.user_id, candidate_id=3, has_seen=True)
                # при нажатии на кнопку "в избранное" помечаем флаг favourite
                elif user_request == "в избранное": # переделать механизм на кнопку
                    write_msg(event.user_id, "Промаркирован favourite") 
                    db.mark_favourite(event.user_id, candidate_id=3, favourite=True)
                elif user_request == "покажи избранное":
                    write_msg(event.user_id, "Список избранных людей")
                    favourite_list = db.show_favourites(event.user_id)
                    # тут функция вывода в чат списка избранных людей
                elif user_request == "пока":
                    write_msg(event.user_id, "Пока!")
                    break
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")

    db.disconnect_db()