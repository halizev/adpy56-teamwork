import psycopg2


class DatingDB:

    def __init__(self, db_name, user_name, password):
        self.db_name = db_name
        self.user_name = user_name
        self.password = password

    def connect_db(self):
        self.conn = psycopg2.connect(database=self.db_name, user=self.user_name, password=self.password)
        self.cur = self.conn.cursor()
    
    # проверка наличия записи в таблице user_vk 
    def check_user_id(self, id):
        self.cur.execute("""
        SELECT EXISTS (SELECT name FROM user_vk WHERE id=%s)
        """, (id,))
        check_id = self.cur.fetchone()
        return check_id[0]
    
    # проверка наличия записи в таблице candidate
    def check_candidate_id(self, id):
        self.cur.execute("""
        SELECT EXISTS (SELECT name FROM candidate WHERE id=%s)
        """, (id,))
        check_id = self.cur.fetchone()
        return  check_id[0]

    # проверка наличия записи в таблице user_vk_candidate
    def check_user_vk_candidate_id(self, user_id, candidate_id):
        self.cur.execute("""
        SELECT EXISTS (SELECT user_vk_id FROM user_vk_candidate 
                        WHERE user_vk_id=%s AND candidate_id=%s);
        """, (user_id, candidate_id))
        check_id = self.cur.fetchone()
        return  check_id[0]

    # добавление записи в таблицу candidate
    def add_user(self, id, first_name, age, gender, city):              
        self.cur.execute("""
        INSERT INTO user_vk(id, name, age, gender, city) VALUES (%s, %s, %s, %s, %s);            
        """, (id, first_name, age, gender, city))        
        self.conn.commit()        
        return 

    # добавление записи в таблицу candidate
    def add_candidate(self, id, first_name, last_name, profile):        
        if self.check_candidate_id(id) is False:
            self.cur.execute("""
            INSERT INTO candidate(id, name, surname, profile_link) VALUES (%s, %s, %s, %s);
            """, (id, first_name, last_name, profile))        
            self.conn.commit()                        
        return 

    # добавление записи в таблицу photo
    def add_photo(self, candidate_id, photo_list):
        for photo_link in photo_list:
            self.cur.execute("""
            INSERT INTO photo(candidate_id, photo_link) VALUES (%s, %s); 
            """, (candidate_id, photo_link))              
        self.conn.commit()        
        return 

    # добавление записи в таблицу user_vk_candidate
    def add_user_vk_candidate(self, user_id, candidate_id, favourite=False, has_seen=False):
        self.cur.execute("""
        INSERT INTO user_vk_candidate(user_vk_id, candidate_id, favourite, has_seen) VALUES (%s, %s, %s, %s)        
        """, (user_id, candidate_id, favourite, has_seen))        
        self.conn.commit()        
        return 
    
    # получение инфо(для критериев поиска) 
    def get_user_info(self, user_id):
        self.cur.execute("""
        SELECT name, age, gender, city FROM user_vk;            
        """, (user_id,))
        return self.cur.fetchall()

    # получение списка кандидатов для отображения пользователю
    def get_candidates(self, user_id):
        self.cur.execute("""
        SELECT c.id, c.name, c.surname, c.profile_link FROM candidate c
        JOIN user_vk_candidate uvc ON c.id = uvc.candidate_id
        WHERE uvc.user_vk_id = %s;          
        """, (user_id,))
        return self.cur.fetchall()       

    # отметить в избранное
    def mark_favourite(self, user_id, candidate_id, favourite=None):
        if favourite is not None:
            self.cur.execute("""
            UPDATE user_vk_candidate SET favourite=%s WHERE user_vk_id=%s AND candidate_id=%s;
            """, (favourite, user_id, candidate_id))
            self.conn.commit() 

    # отметить просмотрено
    def mark_has_seen(self, user_id, candidate_id, has_seen=None):
        if has_seen is not None:
            self.cur.execute("""
            UPDATE user_vk_candidate SET has_seen=%s WHERE user_vk_id=%s AND candidate_id=%s;
            """, (has_seen, user_id, candidate_id))
            self.conn.commit() 

    # формирование списка избранного
    def show_favourites(self, user_id):
        self.cur.execute("""
        SELECT c.id, c.name, c.surname, c.profile_link FROM user_vk_candidate uvc
        JOIN candidate c ON uvc.candidate_id = c.id
        WHERE uvc.favourite is True AND uvc.user_vk_id=%s;
        """, (user_id,))     
                
    def disconnect_db(self):
        self.cur.close()
        self.conn.close()