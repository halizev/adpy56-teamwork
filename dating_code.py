import requests
from datetime import datetime, date


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
            user_bdate = info['bdate']

            return [user_id, user_first_name, user_last_name, user_sex, user_bdate, user_city_id]
    except KeyError:
        print('Ошибка обращения к API')


def search_user_candidates(token_user, id, bdate, sex, city_id):
    url = f'https://api.vk.com/method/users.search'

    user_sex = 0
    if sex == 1:
        user_sex = 2
    elif sex == 2:
        user_sex = 1

    bday = datetime.strptime(bdate, "%d.%m.%Y")
    birthday = bday.date() 
    today = date.today()
    user_age = today.year - birthday.year
    if (today.month < birthday.month or
            (today.month == birthday.month and today.day < birthday.day)):
        user_age = user_age - 1

    params = {'access_token': token_user,
              'user_id': id,
              'v': '5.131',
              'sex': user_sex,
              'age': user_age,
              'city': city_id,
              'fields': 'is_closed, id, first_name, last_name, city, bdate, has_photo',
              'status': '1' or '6',
              'has_photo': '1',
              'count': 100}
           
    candidates = []
    repl = requests.get(url=url, params=params)
    response = repl.json()
    if response.get('response') != None:
        candidates_info = response['response']['items']
        for person_dict in candidates_info:
            if (person_dict['is_closed'] == False) and (person_dict.get('city') != None) and (person_dict['city']['id'] == city_id) and (person_dict['has_photo'] == 1):
                candidate_first_name = person_dict['first_name']
                candidate_last_name = person_dict['last_name']
                candidate_id = str(person_dict['id'])
                candidate_link = 'vk.com/id' + str(person_dict['id'])
                person = {'id': candidate_id, 'first_name': candidate_first_name, 'last_name': candidate_last_name, 'profile': candidate_link}
                candidates.append(person)                
        return candidates    
    else:
        print('Ошибка обращения к API')


def get_candidate_photos(candidate_id, token_user):
    url = f'https://api.vk.com/method/photos.get'
    params = {'access_token': token_user,
              'owner_id': candidate_id,
              'v': '5.131',
              'album_id': 'profile',
              'count': 10,
              'extended': 1}

    photos_list = list()    
    repl = requests.get(url, params=params)
    response = repl.json()
    if response.get('response') is not None:

        for photo in response['response']['items']:
            photo_owner_id = photo['owner_id']
            photo_id = photo['id']
            photo_link = photo['sizes'][-1]['url']
            photo_likes = photo['likes']['count']
            photos_list.append({'photo_id': photo_id, 'photo_owner_id': photo_owner_id, 'photo_likes': photo_likes})
        photo_list_sorted = sorted(photos_list, key=lambda i: i['photo_likes'], reverse=True)
        photos_data = [f"photo{photo['photo_owner_id']}_{photo['photo_id']}" for photo in photo_list_sorted[0:3]]

        return {'candidate_id': candidate_id, 'photo_links': photos_data}