#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2024
#            ✈ https://t.me/kamekuro

# 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit, distribute or redistribute and use for any purpose this file without direct permission from the author.
# All source code is provided for review only.

import httpx
import sqlite3

import netschoolapi as nsapi


class DataBase():
    def __init__(self, filename: str = "db.db"):
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()


    def close(self):
        self.db.close()


    def recvs(self, f, *args):
        self.cursor.execute(f, args)
        return self.cursor.fetchall()

    def save(self, f, *args):
        self.cursor.execute(f, args)
        return self.db.commit()


    def getAllTables(self):
        t = self.recvs("SELECT name FROM sqlite_master WHERE type = 'table'")
        return [i[0] for i in t]

    def getTable(self, table: str):
        tables = self.getAllTables()
        if table not in tables:
            return None
        return self.recvs(f"PRAGMA table_info({table})")


    def regUser(self, uid: int, status: int = 0):
        u = self.getUser(uid)
        if not u:
            self.save(f"""INSERT INTO users (id, status) VALUES (?, ?)""", uid, status)
            u = self.getUser(uid)
        return u

    def getUser(self, uid: int):
        user = self.recvs(f"SELECT * FROM users WHERE id = ?", uid)
        return None if len(user) == 0 else user[0]

    def getNSUser(self, uid: int):
        user = self.recvs(f"SELECT * FROM accounts WHERE id = ?", uid)
        return None if len(user) == 0 else user[0]

    def getAllUsers(self):
        return self.recvs(f"SELECT * FROM users")


    async def getUserNS(self, uid: int) -> nsapi.NetSchoolAPI:
        user = self.getNSUser(uid)
        if not user: return None

        try:
            ns = nsapi.NetSchoolAPI(user[2])
            await ns.login(
                user_name=user[4], password=user[5],
                school_name_or_id=user[3]
            )
            return ns
        except nsapi.errors.NoResponseFromServer:
            raise nsapi.errors.NoResponseFromServer(
                "⚠ <b>«Сетевой Город» вернул ошибку: [No Response From Server].</b>"
            )
        except nsapi.errors.AuthError as e:
            out = f"⚠ <b>«Сетевой Город» вернул ошибку авторизации.</b>"
            if e:
                out = f"⚠ <b>«Сетевой Город» вернул ошибку авторизации</b>" \
                    f"<pre language=\"error\">{e}</pre>"
            raise nsapi.errors.AuthError(out)
        except httpx.HTTPStatusError as e:
            out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку.</b>"
            if e:
                out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку</b>" \
                    f"<pre language=\"error\">{e}</pre>"
            raise nsapi.errors.NetSchoolAPIError(out)