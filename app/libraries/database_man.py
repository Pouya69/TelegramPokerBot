import sqlite3
from sqlite3 import Error


DATABASE_NAME = "database.db"

# SQLite commands

# Users
sqlite_table_command = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        player_id text NOT NULL,
                                        poker_username text,
                                        telegram_username text,
                                        telegram_chat_id text,
                                        payment_link text,
                                        profit real
                                    ); """
sqlite_insert_command = """INSERT INTO users(player_id, poker_username, telegram_username, telegram_chat_id, payment_link, profit)
 VALUES(?,?,?,?,?,?)"""
sqlite_update_command_unique = """UPDATE users
 SET player_id = ?,
 profit = ?
 WHERE player_id = ?"""
sqlite_update_command_global = """UPDATE users
 SET profit = ?
 WHERE poker_username = ?"""
sqlite_update_command_sheets = """UPDATE users
 SET poker_username = ?,
 telegram_username = ?,
 payment_link = ?
 WHERE player_id = ?"""
sqlite_update_command_telegram = """UPDATE users
 SET telegram_chat_id = ?
 WHERE telegram_username = ?"""
sqlite_update_command_telegram_username = """UPDATE users
 SET telegram_username = ?
 WHERE telegram_chat_id = ?"""

# Debts
sqlite_table_command_debts = """ CREATE TABLE IF NOT EXISTS debts (
                                        id integer PRIMARY KEY,
                                        payer text,
                                        receiver text,
                                        amount real
                                    ); """
sqlite_insert_command_debts = """INSERT INTO debts(payer, receiver, amount)
 VALUES(?,?,?)"""
sqlite_update_command_debts = """UPDATE debts
 SET payer = ?,
 receiver = ?,
 amount = ?"""


# Functions
def create_db_connection(first=False):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        if first:
            print("[!] Connecting to SQLITE", sqlite3.version)
        conn = sqlite3.connect(DATABASE_NAME)
        if first:
            print("[+] SQLite connected", sqlite3.version)
    except Error as e:
        print(e)

    return conn


def table_check_users(conn):
    try:
        c = conn.cursor()
        c.execute(sqlite_table_command)
    except Error as e:
        print(e)


def insert_db_users(conn, values):
    # values = (username, tel_username, etc)
    cur = conn.cursor()
    cur.execute(sqlite_insert_command, values)
    conn.commit()


def init_finish_database_users(conn):
    cur = conn.cursor()
    cur.execute("""UPDATE users SET profit = 0.0""")
    conn.commit()


def update_db_users_global(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_global, values)
    conn.commit()


def update_db_users_unique(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_unique, values)
    conn.commit()


def update_db_users_2(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_sheets, values)
    conn.commit()


def update_db_users_set_telegram_username(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_telegram_username, values)
    conn.commit()


def update_db_users_set_telegram_chat_id(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_telegram, values)
    conn.commit()


def select_all_db_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall()
    return rows


def select_one_db_users_telegram(conn, telegram_username):
    row = None
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_username=?", (telegram_username,))
    try:
        row = cur.fetchall()  # row['column_id'] for get the value of a column.
        if cur.rowcount == 0:
            row = None
    except:
        row = None
    return row


def select_one_db_users(conn, player_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE player_id=?", (player_id,))
    row = cur.fetchone()  # row['column_id'] for get the value of a column.
    return row


def select_one_db_users_handle(conn, handle):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE poker_username=?", (handle,))
    row = cur.fetchone()  # row['column_id'] for get the value of a column.
    return row


def delete_all_db_users(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()


def delete_one_db_users(conn, player_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE player_id=?", (player_id,))
    conn.commit()


def table_check_debts(conn):
    try:
        c = conn.cursor()
        c.execute(sqlite_table_command_debts)
    except Error as e:
        print(e)


def insert_db_debts(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_insert_command_debts, values)
    conn.commit()


def update_db_debts(conn, values):
    cur = conn.cursor()
    cur.execute(sqlite_update_command_debts, values)
    conn.commit()


def select_all_db_debts(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM debts")

    rows = cur.fetchall()
    return rows


def select_one_db_debts(conn, payer, receiver):
    cur = conn.cursor()
    cur.execute("SELECT * FROM debts WHERE receiver=? AND payer=?", (receiver, payer))

    row = cur.fetchone()  # row['column_id'] for get the value of a column.
    return row


def delete_all_db_debts(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM debts")
    conn.commit()


def delete_one_db_debts(conn, username):
    cur = conn.cursor()
    cur.execute("DELETE FROM debts WHERE id=?", (username,))
    conn.commit()


def close_db_connection(db):
    db.close()
