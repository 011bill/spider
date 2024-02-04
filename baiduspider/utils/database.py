from baiduspider.settings import DB_CONFIG
import mysql.connector


class MySQL:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def select(self, table, columns, where=None):
        query = "SELECT {} FROM {}".format(', '.join(columns), table)
        if where:
            query += " WHERE {}".format(where)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(["%s"] * len(data))
        query = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, values)
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()

    def update(self, table, data, where):
        set_data = ', '.join(["{}=%s".format(k) for k in data.keys()])
        query = "UPDATE {} SET {} WHERE {}".format(table, set_data, where)
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()

    def delete(self, table, where):
        query = "DELETE FROM {} WHERE {}".format(table, where)
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
