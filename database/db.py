import aiosqlite
DB_NAME = './database/quiz_bot.db'

async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        # Сохраняем изменения
        await db.commit()

async def create_user(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()
async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, current_score INTEGER DEFAULT 0)''')
        # Сохраняем изменения
        await db.commit()
async def add_score(user_id):
    print(user_id)
    print("Добавляем очко!")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET current_score = current_score + 1 WHERE user_id = ?', (user_id,))
        await db.commit()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, current_score FROM quiz_state WHERE user_id = ?", (user_id,)) as cursor:
            print("after add_score:", await cursor.fetchone())

async def get_stat():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, current_score from quiz_state ORDER BY current_score DESC LIMIT 10') as cursor:
            results = ""
            top_scores = await cursor.fetchall()
            for user in top_scores:
                print(user)
                results += f"{user[0]}: {user[1]}\n"
            print(results)
            if results:
                return results
            else:
                return "Пока нет данных по участникам"

