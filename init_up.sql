CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    "name" VARCHAR(255),
    surname VARCHAR(255)
)

CREATE TABLE IF NOT EXISTS contact_phone (
    id SERIAL PRIMARY KEY,
    phone INTEGER NOT NULL UNIQUE,
    phone_type BOOL NOT NULL DEFAULT FALSE,
    confirm BOOL NOT NULL DEFAULT FALSE,
    member_id INTEGER,
    CONSTRAINT fk_member_id
        FOREIGN KEY (member_id)
        REFERENCES members(id)
)

CREATE TABLE IF NOT EXISTS contact_email (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    email_type BOOL NOT NULL DEFAULT FALSE,
    confirm BOOL NOT NULL ,
    member_id INTEGER,
    CONSTRAINT fk_member_id
        FOREIGN KEY (member_id)
        REFERENCES members(id)
)

-- INSERT INTO members ("name", surname) VALUES ("Иван", "Иванович")
-- INSERT INTO contact_phone (phone, phone_type, confirm, member_id) VALUES ("89997775533", 0, 0, 1)
-- INSERT INTO contact_email (email, email_type, confirm, member_id) VALUES ("email@gmail.com", 0, 0, 1)
