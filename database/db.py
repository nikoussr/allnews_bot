import asyncpg



class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    async def connect(self, database_url):
        if not hasattr(self, 'connection'):
            try:
                self.connection = await asyncpg.connect(database_url)
                print(f"Connected successfuly to allnews DB")
            except Exception as e:
                print(e)

    async def disconnect(self):
        if hasattr(self, 'connection'):
            await self.connection.close()
            del self.connection

    async def fetch(self, query, *args):
        if not hasattr(self, 'connection'):
            raise Exception("Database connection is not established.")
        rows = await self.connection.fetch(query, *args)
        mas = []
        for row in rows:
            mas.append(dict(row))
        return mas

    async def execute(self, query, *args):
        if not hasattr(self, 'connection'):
            raise Exception("Database connection is not established.")
        return await self.connection.execute(query, *args)


async def set_themes(db: Database, user_id: int, themes: list[str]):
    for theme in themes:
        await db.execute("INSERT INTO themes (user_id, theme) VALUES($1, $2)", user_id, theme)


async def get_themes(db: Database, user_id: int):
    themes = await db.fetch("SELECT theme FROM themes WHERE user_id = $1", user_id)
    mas = []
    for theme in themes:
        a = theme['theme']
        mas.append(a)
    return mas


async def create_new_user(db: Database, user_id: int, active: bool, date: str, first_name: str, last_name: str,
                          nickname: str):
    await db.execute(
        "INSERT INTO users (user_id, active, date, first_name, last_name, nickname) VALUES ($1, $2, $3, $4, $5, $6)",
        user_id, active, date, first_name, last_name, nickname)


async def user_exists(db: Database, user_id: int):
    return bool(len(await db.fetch("SELECT * FROM users WHERE user_id = $1", user_id)))


async def del_theme(db: Database, user_id: int, theme: str):
    await db.execute("DELETE FROM themes WHERE user_id = $1 AND theme = $2", user_id, theme)


async def change_active(db: Database, user_id: int, active: bool):
    await db.execute("UPDATE users SET active=$1 WHERE user_id=$2", active, user_id)

