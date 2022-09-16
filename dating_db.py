import psycopg2


class DatingDB:

    def __init__(self, db_name, user_name, password):
        self.db_name = db_name
        self.user_name = user_name
        self.password = password

    def connect_db(self):
        self.conn = psycopg2.connect(database=self.db_name, user=self.user_name, password=self.password)
        self.cur = self.conn.cursor()
    
    # проверка наличия записи в таблице client 
    def check_user_id(self, id):
        self.cur.execute("""
        SELECT EXISTS (SELECT first_name FROM client WHERE id=%s)
        """, (id,))
        check_id = self.cur.fetchone()
        return check_id[0]
    
    # проверка наличия записи в таблице candidate
    def check_candidate_id(self, id):
        self.cur.execute("""
        SELECT EXISTS (SELECT first_name FROM candidate WHERE id=%s)
        """, (id,))
        check_id = self.cur.fetchone()
        return  check_id[0]

    # проверка наличия записи в таблице client_candidate
    def check_user_candidate_id(self, user_id, candidate_id):
        self.cur.execute("""
        SELECT EXISTS (SELECT client_id FROM client_candidate 
                        WHERE client_id=%s AND candidate_id=%s);
        """, (user_id, candidate_id))
        check_id = self.cur.fetchone()
        return  check_id[0]

    # добавление записи в таблицу client
    def add_user(self, id, first_name, last_name, sex, bdate, city_id):              
        self.cur.execute("""
        INSERT INTO client(id, first_name, last_name, sex, bdate, city_id) VALUES (%s, %s, %s, %s, %s, %s);            
        """, (id, first_name, last_name, sex, bdate, city_id))        
        self.conn.commit()        
        return 

    # добавление записи в таблицу candidate
    def add_candidate(self, id, first_name, last_name, profile):        
        self.cur.execute("""
        INSERT INTO candidate(id, first_name, last_name, profile_link) VALUES (%s, %s, %s, %s);
        """, (id, first_name, last_name, profile))        
        self.conn.commit()                        
        return 

    # добавление записи в таблицу photo
    def add_photo(self, candidate_id, photo_list):
        for photo_id in photo_list:
            self.cur.execute("""
            INSERT INTO photo(candidate_id, id) VALUES (%s, %s); 
            """, (candidate_id, photo_id))              
        self.conn.commit()        
        return 

    # добавление записи в таблицу client_candidate
    def add_user_candidate(self, user_id, candidate_id, favourite=False, has_seen=False):
        self.cur.execute("""
        INSERT INTO client_candidate(client_id, candidate_id, favourite, has_seen) VALUES (%s, %s, %s, %s)        
        """, (user_id, candidate_id, favourite, has_seen))        
        self.conn.commit()        
        return 
    
    # получение инфо(для критериев поиска) 
    def get_user_info(self, user_id):
        self.cur.execute("""
        SELECT id, sex, bdate, city_id FROM client;            
        """, (user_id,))
        info = self.cur.fetchall()[0]
        if len(info) > 0:
            return {'id': info[0], 'sex': info[1], 'bdate': info[2], 'city_id': info[3]}
        else:
            return None

    # получение списка кандидатов для отображения пользователю
    def get_candidates(self, user_id):
        self.cur.execute("""
        SELECT c.id, c.first_name, c.last_name, c.profile_link, clc.favourite, clc.has_seen FROM candidate c        
        JOIN client_candidate clc ON c.id = clc.candidate_id
        WHERE clc.client_id = %s;          
        """, (user_id,))
        return self.cur.fetchall() 
    
    # получение списка кандидатов для отображения пользователю
    def get_photos(self, candidate_id):
        self.cur.execute("""
        SELECT * FROM photo
        WHERE candidate_id = %s;          
        """, (candidate_id,))
        info = self.cur.fetchall()
        if len(info) > 0:
            return info
        else:
            return None

    # отметить в избранное
    def mark_favourite(self, user_id, candidate_id, favourite=None):
        if favourite is not None:
            self.cur.execute("""
            UPDATE client_candidate SET favourite=%s WHERE client_id=%s AND candidate_id=%s;
            """, (favourite, user_id, candidate_id))
            self.conn.commit() 

    # отметить просмотрено
    def mark_has_seen(self, user_id, candidate_id, has_seen=None):
        if has_seen is not None:
            self.cur.execute("""
            UPDATE client_candidate SET has_seen=%s WHERE client_id=%s AND candidate_id=%s;
            """, (has_seen, user_id, candidate_id))
            self.conn.commit() 

    # формирование списка избранного
    def show_favourites(self, user_id):
        self.cur.execute("""
        SELECT c.id, c.first_name, c.last_name, c.profile_link FROM client_candidate clc
        JOIN candidate c ON clc.candidate_id = c.id
        WHERE clc.favourite is True AND clc.client_id=%s;
        """, (user_id,))     
                
    def disconnect_db(self):
        self.cur.close()
        self.conn.close()