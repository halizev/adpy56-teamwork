from random import randrange
import configparser
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dating_code import get_user_info, search_user_candidates, get_candidate_photos
from dating_db import DatingDB
from utils import generate_keyboard, in_favourite



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

    def write_msg(user_id, message, attachment=None, keyboard=None):
       return vk.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment, 'keyboard': keyboard, 'random_id': randrange(10 ** 7),})

    for event in longpoll.listen():
        
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_request = str(event.text.lower())

                if user_request == "начать":
                    temp_kb = generate_keyboard('Начать')
                    write_msg(event.user_id, 'Вас приветствует бот знакомств! Для поиска людей нажмите "поиск"', keyboard=temp_kb)
                    user_info = get_user_info(event.user_id, token_group)
                    if not db.check_user_id(event.user_id):
                        db.add_user(*user_info)
                elif user_request == "поиск":
                    temp_kb = generate_keyboard('Поиск')
                    write_msg(event.user_id, f"Начинаю поиск людей противоположного пола для знакомства в вашем городе.")
                    user_info = db.get_user_info(event.user_id)
                    candidates_to_db = search_user_candidates(token_user, user_info['id'], user_info['bdate'], user_info['sex'], user_info['city_id'])

                    # если в базе нет кадидата, то создаём запись
                    for candidate in candidates_to_db:
                        if not db.check_candidate_id(candidate['id']):
                            photos = get_candidate_photos(candidate['id'], token_user)
                            if (photos is not None) and (len(photos) > 0):
                                db.add_candidate(**candidate)
                                db.add_photo(photos['candidate_id'], photos['photo_links'])
                                if not db.check_user_candidate_id(user_info['id'], candidate['id']):
                                    db.add_user_candidate(user_info['id'], candidate['id'], favourite=False, has_seen=False)
                    # выводим данные о кандидатах
                    count = 1
                    x = 0
                    candidates_to_view = db.get_candidates(event.user_id)
                    photos_to_view = db.get_photos(candidates_to_view[x][0])
                    first = f"{candidates_to_view[x][1]} {candidates_to_view[x][2]} {candidates_to_view[x][3]}, В избранном: {in_favourite(candidates_to_view[x][4])}"
                    write_msg(event.user_id, f"Найдено: {len(candidates_to_view)}")
                    write_msg(event.user_id, f"{count} {first}", attachment=photos_to_view, keyboard=temp_kb)
                    write_msg(event.user_id, f"Для добавления в избранное нажмите 'в избранное'")
                    write_msg(event.user_id, f"Для просмотра следующего профиля нажмите 'следующий'")
                    write_msg(event.user_id, f"Для корректного завершения работы программы нажмите 'Завершить работу'")
                # при нажатии на кнопку "в избранное" помечаем флаг favourite
                elif user_request == "в избранное":
                    temp_kb = generate_keyboard('В избранное')
                    db.mark_favourite(event.user_id, candidates_to_view[x][0], favourite=True)
                    write_msg(event.user_id, "Добавлено в избранное", keyboard=temp_kb)
                # при нажатии на кнопку "следующий" помечаем флаг has_seen
                elif user_request == "следующий":
                    db.mark_has_seen(event.user_id, candidates_to_view[x][0], has_seen=True)
                    if x == len(candidates_to_view) - 1:
                        write_msg(event.user_id, "Проcмотрены все страницы, соответствующие критериям поиска!")
                        temp_kb = generate_keyboard('Показать избранное')
                        write_msg(event.user_id, "Нажмите 'Показать избранное' для просмотра списка избранных людей.")
                        write_msg(event.user_id, "Или начните новый поиск.", keyboard=temp_kb)
                        write_msg(event.user_id, f"Для корректного завершения работы программы нажмите 'Завершить работу'")
                    else:
                        count += 1
                        x += 1
                        next = f"{candidates_to_view[x][1]} {candidates_to_view[x][2]} {candidates_to_view[x][3]}, В избранном: {in_favourite(candidates_to_view[x][4])}"
                        photos_to_view = db.get_photos(candidates_to_view[x][0])
                        write_msg(event.user_id, f"{count} {next}", attachment=photos_to_view)

                elif user_request == "показать избранное":
                    write_msg(event.user_id, "Список избранных людей: ")
                    favourites_to_view = db.show_favourites(event.user_id)
                    for favourite in favourites_to_view:
                        write_msg(event.user_id, f"{favourite[1]} {favourite[2]} {favourite[3]}")

                elif user_request == "завершить работу":
                    temp_kb = generate_keyboard('Запуск')
                    write_msg(event.user_id, "Работа программы завершена. Для запуска нажмите 'Начать'", keyboard=temp_kb)
                    break
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")

    db.disconnect_db()