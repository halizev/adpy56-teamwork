from random import randrange
from dating_code import get_user_info, search_user_candidates, get_candidate_photos
from dating_db import DatingDB
import configparser
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from pprint import pprint

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

    def write_msg(user_id, message, attachment=None):
       return vk.method('messages.send', {'user_id': user_id, 'message': message,  'attachment': attachment, 'random_id': randrange(10 ** 7),})

    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_request = str(event.text.lower())
                # user_id = str(event.user_id)

                if user_request == "начать": # переделать механизм на кнопку                 
                    user_info = get_user_info(event.user_id, token_group)
                    
                    write_msg(event.user_id, f"Хай, {event.user_id}")
                    if not db.check_user_id(event.user_id):
                        db.add_user(*user_info)                
                elif user_request == "поиск": # переделать механизм на кнопку                   
                    write_msg(event.user_id, f"Начинаю поиск людей противоположного пола для знакомства в вашем городе.")
                    user_info = db.get_user_info(event.user_id)
                    print(user_info)                  
                    candidates_to_db = search_user_candidates(token_user, user_info['id'], user_info['bdate'], user_info['sex'], user_info['city_id'])
                                                             
                    # если в базе нет кадидата, то создаём запись
                    for candidate in candidates_to_db:
                        if not db.check_candidate_id(candidate['id']): 
                            db.add_candidate(**candidate)
                            photos = get_candidate_photos(candidate['id'], token_user)
                            db.add_photo(photos['candidate_id'], photos['list_photo_ids'])
                        if not db.check_user_candidate_id(user_info['id'], candidate['id']):
                            db.add_user_candidate(user_info['id'], candidate['id'], favourite=False, has_seen=False)
                    # выводим данные о кандидатах
                    x = 0
                    candidates_to_show = [candidate for candidate in db.get_candidates(event.user_id)]
                    photos_to_show = db.get_photos(candidates_to_show[x][0])
                    if photos_to_show is not None:
                        att = f'photo{candidates_to_show[x][0]}_{photos_to_show[0][0]}'
                    else:
                        att = None
                    pprint(candidates_to_show)
                    write_msg(event.user_id, f"Найдено: {len(candidates_to_show)}")
                    test = write_msg(event.user_id, f"Первый профиль: {candidates_to_show[x]}", attachment=att)
                    print('возврат' , test)
                    # write_msg(event.user_id, f"Фото {photos_to_show}")
                    write_msg(event.user_id, f"Для добавления в избранное нажмите/напишите 'в избранное'")
                    write_msg(event.user_id, f"Для просмотра следующего профиля нажмите/напишите 'следующий'")
                # при нажатии на кнопку "в избранное" помечаем флаг favourite
                elif user_request == "в избранное": # переделать механизм на кнопку
                    db.mark_favourite(event.user_id, candidates_to_show[x][0], favourite=True)
                    write_msg(event.user_id, "Добавлено в избранное")
                # при нажатии на кнопку "следующий" помечаем флаг has_seen
                elif user_request == "следующий": # переделать механизм на кнопку                                      
                    db.mark_has_seen(event.user_id, candidates_to_show[x][0], has_seen=True)
                    x += 1 
                    photos_to_show = db.get_photos(386540043)
                    if photos_to_show is not None:
                        att = f'photo{candidates_to_show[x][0]}_{photos_to_show[0][0]}'
                    else:
                        att = None
                    write_msg(event.user_id, f"{candidates_to_show[x]}", attachment=att)
                    if x == len(candidates_to_show) - 1:
                        write_msg(event.user_id, "Проcмотрены все страницы, соответствующие критериям поиска")
                        write_msg(event.user_id, "Вы можете просмотреть список избранных людей")                                          
                elif user_request == "покажи избранное": # переделать механизм на кнопку
                    write_msg(event.user_id, "Список избранных людей")
                    favourite_list = db.show_favourites(event.user_id)
                    pprint(favourite_list)
                elif user_request == "пока": # переделать механизм на кнопку
                    write_msg(event.user_id, "Пока!")
                    break
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")

    db.disconnect_db()