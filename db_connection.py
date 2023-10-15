import sqlite3


class Connection():
    __conn=None

    @classmethod
    def get_connection(self):
        if(Connection.__conn==None):
            Connection.__conn=sqlite3.connect('animal_database.db')
        return Connection.__conn



