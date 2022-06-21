import sqlite3

class SQL:
    def __init__(self,db_name):
        self.db = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.db.cursor()

    def execute(self,command,value=None):
        type = command.split(" ")[0].upper()

        if not value:
                out = self.cur.execute(command)
        else:
            out = self.cur.execute(command,value)

        self.db.commit()

        if type == "SELECT":
                fields = next(zip(*out.description))
                values = out.fetchall()
                pairs = [dict(zip(fields,value)) for value in values]
                return pairs
        if type =="INSERT":
            return out.lastrowid
        return



