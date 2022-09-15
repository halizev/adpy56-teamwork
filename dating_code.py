import requests
import dating_db
import datetime



def get_user_info(user_id, token_group):
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
            user_bdate = str(info['bdate'])

            return [user_id, user_first_name, user_last_name, user_bdate, user_sex, user_city_id]
    except KeyError:
        print('get_user_info. Ошибка обращения к API')


def search_user_candidates(user_id, token_user):
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
              '': user_id,
              'v': '5.131',
              'sex': user_sex,
              'age': user_age,
              'city': user_info_array[2],
              'fields': 'is_closed, id, first_name, last_name',
              'status': '1' or '6',
              'has_photo': '1',
              'count': 100}

    try:
        repl = requests.get(url, params=params)
        response = repl.json()
        candidates_info = response['items']
        for person_dict in candidates_info:
            if person_dict['is_closed'] == False:
                candidate_first_name = person_dict['first_name']
                candidate_last_name = person_dict['last_name']
                candidate_id = str(person_dict['id'])
                candidate_link = 'vk.com/id' + str(person_dict['id'])
                dating_db.add_candidate(candidate_id, candidate_first_name, candidate_last_name, candidate_link)
                get_candidate_photos(candidate_id, token_user)
            else:
                continue
        return f'Поиск завершён'
    except KeyError:
        print('search_user_candidates. Ошибка обращения к API')


def get_candidate_photos(candidate_id, token_user):
    url = f'https://api.vk.com/method/photos.get'
    params = {'access_token': token_user,
              'owner_id': candidate_id,
              'v': '5.131',
              'album_id': 'profile',
              'count': 10,
              'extended': 1}

    photos_list = list()
    try:
        repl = requests.get(url, params=params)
        response = repl.json()
        for photo in response['response']['items']:
            photo_link = photo['sizes'][-1]['url']
            photo_likes = photo['likes']['count']
            photos_list.append({'photo_link': photo_link, 'photo_likes': photo_likes})
        sorted(photos_list, key=lambda i: i['likes'], reverse=True)
        dating_db.add_photo(candidate_id, photos_list[0:3])
    except KeyError:
        print('get_candidate_photos. Ошибка обращения к API')

