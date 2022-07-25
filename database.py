import sqlite3
import psycopg2
from config import host, user, password, db_name

from aiogram.types import Message


def create_db():
    global base, cur
    try:
        base = psycopg2.connect(
            host=host,
            user=user,
            password=password
        )
        base.autocommit = True
        with base.cursor() as cur:
            cur.execute('CREATE database schedule_bot')
        print('Database created')
    except psycopg2.errors.DuplicateDatabase as dd:
        print('Database exists')
    finally:
        if base:
            cur.close()


def sql_start():
    global base, cur
    base = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    base.autocommit = False
    cur = base.cursor()
    if base:
        print('database connected')
    else:
        cur.execute('CREATE database schedule_bot')
    cur.execute('CREATE TABLE IF NOT EXISTS schedule(event_name varchar(50) NOT NULL,\
            event_start TIMESTAMP NOT NULL, event_end TIMESTAMP NOT NULL, user_id integer NOT NULL, PRIMARY KEY(event_name, user_id))')
    cur.execute('CREATE TABLE IF NOT EXISTS timezone(user_id integer NOT NULL PRIMARY KEY, tz TEXT)')
    cur.close()


def user_exists(userid):
    cursor = base.cursor()
    cursor.execute(f'SELECT * FROM timezone WHERE user_id = %s', (str(userid), ))
    res = cursor.fetchmany(1)
    cursor.close()
    return bool(len(res))


async def add_users(userid):
    cursor = base.cursor()
    cursor.execute("INSERT INTO timezone VALUES(%s, %s)", (userid, '3'))
    base.commit()
    cursor.close()


async def change_timezone_in_db(userid, timezone):
    cursor = base.cursor()
    cursor.execute("""
                    UPDATE timezone
                    SET tz=%s
                    WHERE user_id=%s
                    """, (str(timezone), str(userid)))
    base.commit()
    cursor.close()


def get_utc(userid):
    cursor = base.cursor()
    cursor.execute(f'SELECT tz FROM timezone WHERE user_id=%s', (str(userid), ))
    res = cursor.fetchmany(1)
    print(res)
    cursor.close()
    return res[0][0]


async def add_record(state):
    cursor = base.cursor()
    async with state.proxy() as data:
        cursor.execute('INSERT INTO schedule VALUES(%s, %s, %s, %s)', tuple(data.values()))
        base.commit()
    cursor.close()


def get_all_records_by_userid(userid):
    cursor = base.cursor()
    cursor.execute(f'SELECT * FROM schedule WHERE user_id = %s', (str(userid), ))
    rows = cursor.fetchall()
    all_events = []
    res = ''
    for row in rows:
        all_events.append(row[:-1])
    for element in all_events:
        res += f'{int(all_events.index(element) + 1)}. Event name: {element[0]}, \n Time: {element[1]} - {element[2]} \n'
    cursor.close()
    return res, rows


async def del_record(userid, eventname):
    cursor = base.cursor()
    cursor.execute(f'DELETE FROM schedule WHERE user_id = %s AND event_name = %s', (str(userid), str(eventname)))
    base.commit()
    cursor.close()


async def edit_record(state, userid, eventname):
    cursor = base.cursor()
    async with state.proxy() as data:
        cursor.execute("""
                    UPDATE schedule
                    SET event_name=%s, event_start=%s, event_end=%s 
                    WHERE user_id = %s AND event_name = %s
                    """,
                       (tuple(data.values())[0], tuple(data.values())[1], tuple(data.values())[2], userid,
                        str(eventname)))
        base.commit()
    cursor.close()
