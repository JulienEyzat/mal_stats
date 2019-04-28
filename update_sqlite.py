import sqlite3

def init_connection():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    return conn, c

def is_table(c, table_name):
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if c.fetchone():
        return True
    else:
        return False

def create_table(c, table_name):
    c.execute("CREATE TABLE '%s' (date, anime_name, anime_members, anime_score, PRIMARY KEY (date, anime_name))" %(table_name))

def drop_table(c, table_name):
    c.execute("DROP TABLE IF EXISTS '%s'" %(table_name))

def update_table(conn, c, table_name, data):
    values_to_insert = []
    for anime in data:
        values_to_insert.append([anime['date'], anime['anime_name'], anime['anime_members'], anime['anime_score']])
    c.executemany("INSERT OR REPLACE INTO '%s' (date, anime_name, anime_members, anime_score) VALUES (?, ?, ?, ?)" %(table_name), values_to_insert)
    conn.commit()

def update_sqlite(year, season, data):
    conn, c = init_connection()
    table_name = '%s_%s' %(year, season)
    if not is_table(c, table_name):
        create_table(c, table_name)

    update_table(conn, c, table_name, data)
