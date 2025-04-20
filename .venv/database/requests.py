import aiosqlite
import random
import asyncio
import sqlite3
from datetime import date, datetime
from typing import Optional, Dict, Union, Tuple, List
import json
from aiosqlite import connect
from keyboards.inline import tasks_kb
from lexicon.lexicon import LEXICON_RU

actual_date = date.today().strftime("%Y-%m-%d")
first_task = LEXICON_RU['default_task']
DATABASE_FILE = 'database.sqlite'


async def database_on():
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        await db.execute(
            '''CREATE TABLE IF NOT EXISTS tasks(
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            video TEXT
            )
            '''
        )

        await db.execute(
            '''CREATE TABLE IF NOT EXISTS users 
            (user_id int primary key, 
            chat_id int, 
            user_name varchar(50), 
            balance int CHECK (balance >= 0),
            date_of_last_given_task varchar(10),
            active_task_id int,
            completed_tasks TEXT DEFAULT '[]',
            FOREIGN KEY (active_task_id) REFERENCES tasks (task_id)
            )
            '''
        )

        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)"
        )

        await db.commit()


async def check_db_structure():
    """Проверяет и обновляет структуру БД при необходимости"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Проверяем наличие колонки completed_tasks
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in await cursor.fetchall()]

        if 'completed_tasks' not in columns:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN completed_tasks TEXT DEFAULT '[]'")
                await db.commit()
                print("Добавлена колонка completed_tasks в таблицу users")
            except Exception as e:
                print(f"Ошибка при добавлении колонки: {e}")

async def add_user(
        user_id: int,
        chat_id: int,
        user_name: str,
        balance: int = 0,
        date_of_last_given_task: str = actual_date,
        active_task_id: int = 1,
        completed_tasks: list = None
):
    """Добавляет или обновляет пользователя с проверкой структуры БД"""
    if completed_tasks is None:
        completed_tasks = []

    # Преобразуем список в JSON-строку
    completed_tasks_json = json.dumps(completed_tasks)

    async with aiosqlite.connect(DATABASE_FILE) as db:
        try:
            # Сначала проверяем структуру
            await check_db_structure()

            # Пробуем вставить нового пользователя
            await db.execute(
                '''INSERT INTO users 
                (user_id, chat_id, user_name, balance, 
                 date_of_last_given_task, active_task_id, completed_tasks) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, chat_id, user_name, balance,
                 date_of_last_given_task, active_task_id, completed_tasks_json)
            )
        except aiosqlite.IntegrityError:
            pass
        await db.commit()


async def add_task(text: str, video_path: str) -> Optional[int]:
    """Добавляет новую задачу и возвращает её ID"""
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            cursor = await db.execute(
                "INSERT INTO tasks (text, video) VALUES (?, ?)",
                (text, video_path)
            )
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при добавлении задачи: {e}")
        return None


async def get_last_task_date(user_id: int) -> str | None:
    """Получает дату последнего выданного задания из БД"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            'SELECT date_of_last_given_task FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None


async def is_task_given_today(user_id: int) -> bool:
    """Проверяет, выдавалось ли задание пользователю сегодня"""
    last_date_str = await get_last_task_date(user_id)
    if not last_date_str:
        return False

    today = datetime.now().strftime('%Y-%m-%d')
    return last_date_str == today

async def set_active_task(user_id: int, new_task_id: int):
    """Устанавливает активное задание для пользователя

    Args:
        user_id: ID пользователя
        new_task_id: ID нового задания (или None, чтобы сбросить активное задание)
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Проверяем существование задания (если new_task_id не None)
        if new_task_id is not None:
            cursor = await db.execute(
                'SELECT 1 FROM tasks WHERE task_id = ?',
                (new_task_id,)
            )
            if not await cursor.fetchone():
                raise ValueError(f"Задание с ID {new_task_id} не существует")

        # Обновляем активное задание пользователя
        await db.execute(
            'UPDATE users SET active_task_id = ? WHERE user_id = ?',
            (new_task_id, user_id)
        )
        await db.commit()

async def get_random_task_id() -> Optional[int]:
    """Возвращает случайный task_id"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute('SELECT task_id FROM tasks') as cursor:
            task_ids = [row[0] async for row in cursor]
            return random.choice(task_ids) if task_ids else None

async def get_random_task() -> tuple[int, str, str] | None:
    """Возвращает (task_id, text, video) или None, если заданий нет"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            '''SELECT task_id, text, video FROM tasks 
            ORDER BY RANDOM() LIMIT 1'''
        )
        return await cursor.fetchone()

async def get_task_text(task_id: int) -> Optional[str]:
    """Возвращает текст задачи по ID"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute('SELECT text FROM tasks WHERE task_id = ?', (task_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def get_task_video(task_id: int) -> Optional[str]:
    """Возвращает VIDEO задачи по ID"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute('SELECT video FROM tasks WHERE task_id = ?', (task_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def increase_balance(user_id: int, amount: int):
    """Пополняет баланс пользователя"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            'UPDATE users SET balance = balance + ? WHERE user_id = ?',
            (amount, user_id)
        )
        await db.commit()

async def get_balance(user_id: int) -> Optional[int]:
    """Возвращает баланс пользователя"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def clear_active_task(user_id: int):
    """Сбрасывает активную задачу пользователя"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            'UPDATE users SET active_task_id = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()

async def get_active_task(user_id: int) -> Optional[Dict[str, Union[int, str]]]:
    """Возвращает активную задачу пользователя"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute(
            'SELECT active_task_id FROM users WHERE user_id = ?',
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()

        if not result or result[0] is None:
            return None

        async with db.execute(
            'SELECT task_id, text, video FROM tasks WHERE task_id = ?',
            (result[0],)
        ) as cursor:
            task_data = await cursor.fetchone()

        return {
            'task_id': task_data[0],
            'text': task_data[1],
            'video': task_data[2]
        } if task_data else None

async def user_exists(user_id: int) -> bool:
    """Проверяет существование пользователя"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def get_username_by_id(user_id: int) -> Optional[str]:
    """Возвращает имя пользователя по ID"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute(
            "SELECT user_name FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def clear_table(table_name: str) -> bool:
    """Очищает указанную таблицу"""
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute(f"DELETE FROM {table_name}")
            try:
                await db.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_name}'")
            except aiosqlite.OperationalError:
                pass
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при очистке таблицы {table_name}: {e}")
        return False

async def delete_row_by_id(table_name: str, id_value: int) -> bool:
    """Удаляет строку из таблицы по ID"""
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            id_column = "user_id" if table_name == "users" else "task_id"
            await db.execute(
                f"DELETE FROM {table_name} WHERE {id_column} = ?",
                (id_value,)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении: {e}")
        return False

async def get_completed_tasks(user_id: int) -> list[int]:
    """Возвращает список с ID выполненных заданий"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute(
            "SELECT completed_tasks FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if result and result[0]:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return []
            return []

async def add_completed_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        current = await get_completed_tasks(user_id)
        new_tasks = list(current) + [task_id]
        await db.execute(
            "UPDATE users SET completed_tasks = ? WHERE user_id = ?",
            (json.dumps(new_tasks), user_id)
        )
        await db.commit()

async def get_all_user_ids() -> List[int]:
    """Получает все user_id из базы данных"""
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                return [row[0] async for row in cursor]
    except Exception as e:
        print(f"Ошибка при получении user_ids: {e}")
        return []

async def get_all_chat_ids() -> Tuple[int, ...]:
    """
    Возвращает кортеж всех chat_id из базы данных
    :return: Кортеж с chat_id пользователей
    """
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            async with db.execute("SELECT chat_id FROM users") as cursor:
                return tuple(row[0] for row in await cursor.fetchall())
    except Exception as e:
        print(f"Ошибка при получении chat_ids: {e}")
        return tuple()

async def get_all_users_data() -> List[Dict]:
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Устанавливаем row_factory для доступа к колонкам по имени
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM users") as cursor:
            users = []
            async for row in cursor:
                # Преобразуем каждую строку в словарь
                user_data = dict(row)

                # Преобразуем completed_tasks из JSON строки в список
                if 'completed_tasks' in user_data and user_data['completed_tasks']:
                    try:
                        user_data['completed_tasks'] = json.loads(user_data['completed_tasks'])
                    except json.JSONDecodeError:
                        user_data['completed_tasks'] = []
                else:
                    user_data['completed_tasks'] = []

                users.append(user_data)

            return users