import psycopg2

params = {
    "database": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost"
}

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                "name" VARCHAR(255),
                surname VARCHAR(255)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS contact_phone (
                id SERIAL PRIMARY KEY,
                phone BIGINT NOT NULL UNIQUE,
                phone_type BOOL NOT NULL DEFAULT FALSE,
                confirm BOOL NOT NULL DEFAULT FALSE,
                member_id INTEGER,
                CONSTRAINT fk_member_id
                    FOREIGN KEY (member_id)
                    REFERENCES members(id) ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS contact_email (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                email_type BOOL NOT NULL DEFAULT FALSE,
                confirm BOOL NOT NULL DEFAULT FALSE,
                member_id INTEGER,
                CONSTRAINT fk_member_id
                    FOREIGN KEY (member_id)
                    REFERENCES members(id) ON DELETE CASCADE
            );
        """)
    
    print("Таблицы созданы")

def add_client(conn, name, surname, phone=None, email=None):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO members (name, surname) VALUES (%s, %s) RETURNING id;', 
            (name, surname)
            )

        member_id = cur.fetchone()[0]
        
        if phone is not None:
            cur.execute(
                'INSERT INTO contact_phone (phone, member_id) VALUES (%s, %s);', 
                (phone, member_id)
                )

        if email is not None:
            cur.execute(
                'INSERT INTO contact_email (email, member_id) VALUES (%s, %s);',
                (email, member_id)
            )

    print(f"Пользователь {name} успешно добавлен с ID {member_id}")

def add_phone(conn, member_id, phone):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO contact_phone (phone, member_id) VALUES (%s, %s);', 
            (phone, member_id)
        )

def add_email(conn, member_id, email):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO contact_email (email, member_id) VALUES (%s, %s);',
            (email, member_id)
        )

def change_client(conn, member_id=None, name=None, surname=None, phone_id=None, phone=None, email_id=None, email=None):
    with conn.cursor() as cur:
        if name is not None:
            cur.execute('UPDATE members SET name = %s WHERE id = %s;', 
                (name, member_id)            
            )
        
        if surname is not None:
            cur.execute('UPDATE members SET surname = %s WHERE id = %s;', 
                (surname, member_id)            
            )
        
        if phone_id is not None:
             cur.execute('UPDATE contact_phone SET phone = %s WHERE id = %s;', 
                (phone, phone_id)            
            )
        if email_id is not None:
            cur.execute('UPDATE contact_email SET email = %s WHERE id = %s;', 
                (email, email_id)            
            )
             
    print(f"Данные клиента {member_id} обновлены")

def del_phone(conn, phone_id, phone):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM contact_phone WHERE id = %s and phone = %s;', 
            (phone_id, phone)
        )
    
    print(f"Данные клиента {phone} удалены")

def del_email(conn, email_id, email):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM contact_email WHERE id = %s and email = %s;', 
            (email_id, email)
        )
    
    print(f"Данные клиента {email} удалены")

def del_client(conn, member_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM members WHERE id = %s;", (member_id))
    
    print(f"Клиент {member_id} и все его контакты удалены одной командой")

def search_client(conn, name=None, surname=None, phone=None, email=None):
    with conn.cursor() as cur:
        query = """
            SELECT DISTINCT m.id, m.name, m.surname 
            FROM members m
            LEFT JOIN contact_phone p ON m.id = p.member_id
            LEFT JOIN contact_email e ON m.id = e.member_id
            WHERE (%s IS NULL OR m.name = %s)
              AND (%s IS NULL OR m.surname = %s)
              AND (%s IS NULL OR p.phone = %s)
              AND (%s IS NULL OR e.email = %s);
        """

        cur.execute(query, (name, name, surname, surname, phone, phone, email, email))
        
        return cur.fetchall()

with psycopg2.connect(**params) as conn:
    create_db(conn)

    # 2. Добавление клиента (add_client)
    add_client(conn, "Иван", "Иванов", 79991234567, "ivan@mail.ru")
    
    # Получим его ID для следующих тестов (обычно это 1)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM members WHERE name='Иван';")
        user_id = cur.fetchone()[0]

    # 3. Добавление дополнительного телефона (add_phone)
    add_phone(conn, user_id, 79001112233)

    # 4. Добавление дополнительной почты (add_email)
    add_email(conn, user_id, "ivan_work@example.com")

    # 5. Поиск клиента (search_client)
    print("Результат поиска:", search_client(conn, surname="Иванов", phone=79001112233))

    # 6. Изменение данных клиента (change_client)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contact_email WHERE email='ivan@mail.ru';")
        e_id = cur.fetchone()[0]
    
    change_client(conn, member_id=user_id, surname="Петров", email_id=e_id, email="petrov@mail.ru")

    # 7. Удаление конкретного телефона (del_phone)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contact_phone WHERE phone=79001112233;")
        p_id = cur.fetchone()[0]
    del_phone(conn, p_id, 79001112233)

    # 8. Удаление конкретной почты (del_email)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contact_email WHERE email='ivan_work@example.com';")
        e_id_work = cur.fetchone()[0]
    del_email(conn, e_id_work, "ivan_work@example.com")

    # 9. ПОЛНОЕ УДАЛЕНИЕ КЛИЕНТА (del_client)
    def del_client_fixed(conn, member_id):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM members WHERE id = %s;", (member_id,))
        print(f"Клиент {member_id} полностью удален")

    del_client_fixed(conn, user_id)

    # Проверка: поиск должен вернуть пустой список
    print("Проверка после удаления:", search_client(conn, name="Иван"))

print("\nТест завершен успешно!")

conn.close()