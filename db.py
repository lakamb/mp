import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('mp.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS Profile(user_id TEXT, wb_token TEXT, from_dt TEXT, extra_field TEXT)")

    db.commit()

async def create_profile(user_id):
    user = cur.execute("SELECT * FROM Profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO Profile VALUES(?, ?, ?, ?)", (user_id, '', '', ''))

async def edit_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE Profile SET wb_token = '{}', from_dt = '{}', extra_field = '{}' WHERE user_id == '{}' ".format(data['wb_token'], data['from_dt'], '', user_id))
        db.commit()
