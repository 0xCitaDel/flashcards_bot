import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import (
    Bot,
    Dispatcher,
    executor,
    types
)
from aiogram.utils.markdown import hspoiler
from aiogram.dispatcher import FSMContext
import logging
import sqlite3
import random

ADMINS = [979834772, 940485267]
API_TOKEN = os.getenv('API_BOT')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect('fc.db')
cursor = connection.cursor()

# Create database

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS words(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_en TEXT NOT NULL,
    word_ru TEXT NOT NULL,
    word_id INTEGER REFERENCES words_info(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS words_info(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    lesson TEXT
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS favourites_word(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_word INTEGER REFERENCES words(id),
    user_id INTEGER REFERENCES users(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    name TEXT
    );
    """
)
connection.commit()


"""
    Keyboards
"""

"""Button for main menu"""
cancel_btn = InlineKeyboardButton('◀ Отмена', callback_data='state_exit')
btn_state_exit = [cancel_btn]

btn_main_menu = [
    InlineKeyboardButton('🧠 Начать тренировку 🧠',
                         callback_data='app_choice_card'),
    InlineKeyboardButton('🌐 Незнальная 🌐', callback_data='app_repeat_cards'),
    InlineKeyboardButton('👀 Показать все карточки 👀',
                         callback_data='get_all_cards'),
    InlineKeyboardButton('⚙ Настройки ⚙', callback_data='settings_callback')
]


"""Button for training flash card"""
btn_tarin_go = [InlineKeyboardButton(
    'Начнем?', callback_data='app_start_card'), cancel_btn]
btn_tarin_end = [InlineKeyboardButton(
    'Готово 🏁', callback_data='app_train_pagination_en_true')]
btn_train_next_en = [
    InlineKeyboardButton(
        '❌ False', callback_data='app_train_pagination_en_false'),
    InlineKeyboardButton(
        'True ✅', callback_data='app_train_pagination_en_true'),
    cancel_btn,
]
btn_train_next_ru = [
    InlineKeyboardButton(
        '❌ False', callback_data='app_train_pagination_ru_false'),
    InlineKeyboardButton(
        'True ✅', callback_data='app_train_pagination_ru_true'),
    cancel_btn,
]
btn_select_lang = [
    InlineKeyboardButton('🇷🇺 (RUS) -> (ENG)🇺🇸', callback_data='rutoen'),
    InlineKeyboardButton('🇺🇸 (ENG) -> (RUS) 🇷🇺', callback_data='entoru'),
    cancel_btn,
]

"""Button for settings"""
btn_select_settings = [
    InlineKeyboardButton('➕ Добавить карточку',
                         callback_data='setting_add_card'),
    InlineKeyboardButton('➕ Добавить тему', callback_data='setting_add_theme'),
    InlineKeyboardButton('📗 Изменть карточку',
                         callback_data='setting_change_card'),
    InlineKeyboardButton(
        '📔 Изменть тему', callback_data='setting_change_theme'),
    InlineKeyboardButton('❌ Отмена', callback_data='none'),
]

btn_back_settings = InlineKeyboardButton(
    '🔙 Вернутсья в настрйки', callback_data='settings_callback')
btn_settings_repeat_theme = [
    InlineKeyboardButton('➕ Добавить еще одну тему',
                         callback_data='setting_add_theme'),
    btn_back_settings
]

btn_settings_repeat_card = [
    InlineKeyboardButton('➕ Добавить еще одну карточку',
                         callback_data='setting_add_card'),
    btn_back_settings
]

btn_settings_change_theme = [
    InlineKeyboardButton('➕ Изменить еще одну тему',
                         callback_data='setting_change_theme'),
    btn_back_settings

]

btn_settings_change_card = [
    InlineKeyboardButton('➕ Изменить еще одну карточку',
                         callback_data='setting_change_card'),
    btn_back_settings
]

# Keyboard
kb_main_menu = InlineKeyboardMarkup(row_width=1).add(*btn_main_menu)
kb_state_exit = InlineKeyboardMarkup(row_width=1).add(*btn_state_exit)
kb_train_pagination_exstart = InlineKeyboardMarkup(
    row_width=1).add(*btn_tarin_go)
kb_train_pagination_exend = InlineKeyboardMarkup(
    row_width=1).add(*btn_tarin_end)
kb_train_pagination_en = InlineKeyboardMarkup(
    row_width=2).add(*btn_train_next_en)
kb_train_pagination_ru = InlineKeyboardMarkup(
    row_width=2).add(*btn_train_next_ru)
kb_select_lang = InlineKeyboardMarkup(row_width=2).add(*btn_select_lang)
kb_select_settings = InlineKeyboardMarkup(
    row_width=2).add(*btn_select_settings)
kb_settings_repeat_theme = InlineKeyboardMarkup(
    row_width=1).add(*btn_settings_repeat_theme)
kb_settings_repeat_card = InlineKeyboardMarkup(
    row_width=1).add(*btn_settings_repeat_card)
kb_settings_change_theme = InlineKeyboardMarkup(
    row_width=1).add(*btn_settings_change_theme)
kb_settings_change_card = InlineKeyboardMarkup(
    row_width=1).add(*btn_settings_change_card)

btn_repeat_select_lang = [
    InlineKeyboardButton('🇷🇺 (RUS) -> (ENG) 🇺🇸',
                         callback_data='repeat_rutoen'),
    InlineKeyboardButton('🇺🇸 (ENG) -> (RUS) 🇷🇺',
                         callback_data='repeat_entoru'),
    cancel_btn,
]
kb_repeat_select_lang = InlineKeyboardMarkup(
    row_width=2).add(*btn_repeat_select_lang)


btn_repeat_next_en = [
    InlineKeyboardButton('❌ False en repeat',
                         callback_data='app_repeat_pagination_en_false'),
    InlineKeyboardButton(
        'True ✅', callback_data='app_repeat_pagination_en_true'),
    cancel_btn,
]

btn_repeat_next_ru = [
    InlineKeyboardButton('❌ False ru repeat',
                         callback_data='app_repeat_pagination_ru_false'),
    InlineKeyboardButton(
        'True ✅', callback_data='app_repeat_pagination_ru_true'),
    cancel_btn,
]

kb_repeat_pagination_en = InlineKeyboardMarkup(
    row_width=2).add(*btn_repeat_next_en)
kb_repeat_pagination_ru = InlineKeyboardMarkup(
    row_width=2).add(*btn_repeat_next_ru)

# FSMachine


class FSMChoiceThemeSingle(StatesGroup):
    """
    State for training flash cards
    """
    theme = State()


class FSMCardPagination(StatesGroup):
    """
    State after state FSMChoiceThemeSingle
    """
    card = State()


class FSMChoiceThemeAll(StatesGroup):
    """
    State for show all cards in the theme
    """
    theme = State()


class FSMRepatCards(StatesGroup):
    """
    State for show all repeat cards by ID in the theme
    """
    card = State()


class FSMSettingAddCard(StatesGroup):
    """
    State for adding a new card in to data base
    befor FSMSettingAddCardItems State
    """
    choice_theme = State()


class FSMSettingAddCardItems(StatesGroup):
    """
    State for adding a new card in to data base
    """
    word_en = State()
    word_ru = State()


class FSMSettingAddTheme(StatesGroup):
    """
    State for adding a new theme in to data base
    """
    titile = State()
    lesson = State()


class FSMSettingChangeTheme(StatesGroup):
    """
    State for change a theme from data base
    """
    id_theme = State()
    title_word = State()
    lesson = State()


class FSMSettingChangeCard(StatesGroup):
    """
    State for change a theme from data base
    """
    id_card = State()
    word_en = State()
    word_ru = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Entry handler point function
    """
    user_name = message.from_user.username
    user_id = message.from_id
    if user_id in ADMINS:
        await message.answer(
            text=f'Привет, {user_name}, давай начнем',
            reply_markup=kb_main_menu
        )
    else:
        await message.answer(
            text='⚠ Отказано в доступе'
        )


@dp.callback_query_handler(lambda c: c.data == 'none')
async def menu_callback_none(callback: types.CallbackQuery):
    """
    Ex-entry callback point function
    """
    await callback.message.edit_text(
        text='Что будем делать дальше?',
        reply_markup=kb_main_menu
    )

# Set for async function 'get_callback_cards'
callback_queries = [
    'app_choice_card',          # Start train callback
    'get_all_cards',            # Show all the cards callback
    'setting_add_card',         # Add new card
    'setting_change_theme'      # Change old theme
]


@dp.callback_query_handler(lambda c: c.data in callback_queries)
async def get_callback_cards(callback: types.CallbackQuery):
    """
    This function is common to subsequent states
    """
    query = cursor.execute('SELECT * FROM words_info;')
    connection.commit()
    data = ''
    for i in query:
        data += f'№{i[0]} - {i[1]} ({i[2]} урок)\n'
    await callback.message.edit_text(
        text=f'Отправьте ID урока\n\n{data}',
        reply_markup=kb_state_exit
    )
    if callback.data == 'app_choice_card':
        await FSMChoiceThemeSingle.theme.set()
    elif callback.data == 'get_all_cards':
        await FSMChoiceThemeAll.theme.set()
    elif callback.data == 'setting_add_card':
        await FSMSettingAddCard.choice_theme.set()
    elif callback.data == 'setting_change_theme':
        await FSMSettingChangeTheme.id_theme.set()


@dp.message_handler(state=FSMChoiceThemeSingle.theme)
async def get_card(message: types.Message, state: FSMContext):
    """
    Function for generating flash cards
    """
    if message.text.isdigit():
        id = message.text
        query = cursor.execute(f"SELECT * FROM words WHERE word_id = {id};")
        connection.commit()
        await state.finish()
        await FSMCardPagination.card.set()
        async with state.proxy() as data:
            data['card_array'] = [i for i in query]
            data['card_true'] = []
            data['card_false'] = []
            data['count'] = 0
            random.shuffle(data['card_array'])
            await message.answer(
                text=f"🃏 Всего надо пройти {len(data['card_array'])} карточек, удачи!",
                reply_markup=kb_select_lang
            )
    else:
        await message.answer(
            text="⚠ Надо ввести положительное число",
            reply_markup=kb_state_exit
        )


@dp.callback_query_handler(lambda c: c.data == 'app_repeat_cards')
async def get_card_repeat(callback: types. CallbackQuery, state: FSMContext):
    """
    Function for repeat General cards
    """
    user_id = callback.from_user.id
    await FSMRepatCards.card.set()
    query = cursor.execute(
        f"""
        SELECT 
            words.id,
            words.word_en, 
            words.word_ru ,
            users.tg_id
        FROM 
            favourites_word 
        INNER JOIN 
            words
        ON
            favourites_word.id_word = words.id
        INNER JOIN 
            users
        ON
            favourites_word.user_id = users.id
        WHERE 
            tg_id = {user_id} ;
        """).fetchall()
    connection.commit()
    async with state.proxy() as data:
        data['card_array'] = query
        data['card_true'] = []
        data['card_false'] = []
        data['count'] = 0
        len_card = len(data['card_array'])
    await callback.message.edit_text(
        text=f"Всего надо отточить {len_card} карточек, удачи!",
        reply_markup=kb_repeat_select_lang
    )

callback_repeat_data = [
    'repeat_rutoen',
    'repeat_entoru',
    'app_repeat_pagination_en_true',
    'app_repeat_pagination_en_false',
    'app_repeat_pagination_ru_true',
    'app_repeat_pagination_ru_false'
]


@dp.callback_query_handler(lambda c: c.data in callback_repeat_data, state=FSMRepatCards.card)
async def state_card_repeat(callback: types.CallbackQuery, state: FSMContext):
    """
    A general function for RU and ENG pagination repeat cards.
    """
    async with state.proxy() as data:
        mess = data['card_array']
        len_mess = len(mess)
        cnt = data['count']

        if callback.data in ['app_repeat_pagination_en_true', 'app_repeat_pagination_ru_true']:
            data['card_true'].append(mess[cnt - 1])
        elif callback.data in ['app_repeat_pagination_en_false', 'app_repeat_pagination_ru_false']:
            data['card_false'].append(mess[cnt - 1])

        card_true = data['card_true']
        card_false = data['card_false']
        len_card_true = len(card_true)
        if cnt == 0:
            correct_answer = 0
        else:
            correct_answer = int((len_card_true/cnt)*100)

        if len(data['card_array']) != data['count']:
            en_callback = [
                'repeat_entoru', 'app_repeat_pagination_en_true', 'app_repeat_pagination_en_false']
            ru_callback = [
                'repeat_rutoen', 'app_repeat_pagination_ru_true', 'app_repeat_pagination_ru_false']
            if callback.data in en_callback:
                hidden_text = hspoiler(f'{mess[cnt][2]}')
                await callback.message.answer(
                    text=f'{cnt+1}/{len_mess} (#{mess[cnt][0]})\n\n'
                    f'{mess[cnt][1]}\n\n{hidden_text}\n\n'
                    f'🔴 {len(card_false)} - {len(card_true)} 🟢'
                    f' ({correct_answer}%)',
                    reply_markup=kb_repeat_pagination_en
                )
                await callback.message.delete()
                data['count'] += 1
            elif callback.data in ru_callback:
                hidden_text = hspoiler(f'{mess[cnt][1]}')
                await callback.message.answer(
                    text=f'{cnt+1}/{len_mess} (#{mess[cnt][0]})\n\n'
                    f'{mess[cnt][2]}\n\n{hidden_text}\n\n'
                    f'🔴 {len(card_false)} - {len(card_true)} 🟢'
                    f' ({correct_answer}%)',
                    reply_markup=kb_repeat_pagination_ru
                )
                await callback.message.delete()
                data['count'] += 1
        else:
            card_false_string = ''
            user_id = callback.from_user.id
            query = cursor.execute('''
                            SELECT favourites_word.id_word, users.tg_id 
                            FROM favourites_word 
                            INNER JOIN users
                            ON favourites_word.user_id = users.id;'''
                                   ).fetchall()
            id_user_id = cursor.execute(
                f'''SELECT id FROM users WHERE tg_id = {user_id}''').fetchone()
            connection.commit()
            for phrase in data['card_false']:
                card_false_string += f'#{phrase[0]}: {phrase[1]} - {phrase[2]}\n'
            await callback.message.edit_text(
                text=f"Фразы которые стоит повторить\n{card_false_string}",
                reply_markup=kb_main_menu
            )
            for k in data['card_true']:
                cursor.execute(
                    f"""DELETE FROM favourites_word WHERE id_word = {k[0]} AND user_id = {id_user_id[0]};""")
                connection.commit()
            await state.finish()

# Set for async function 'callback_point'
callback_pagination = [
    'app_train_pagination_ru_true',         # Pagination callback RU true
    'app_train_pagination_ru_false',        # Pagination callback RU false
    'rutoen',                               # Foreign point callback RU
    'app_train_pagination_en_true',         # Pagination callback ENGntrue
    'app_train_pagination_en_false',        # Pagination callback ENG false
    'entoru',                               # Foreign point callback ENG
]


@dp.callback_query_handler(lambda c: c.data in callback_pagination, state=FSMCardPagination.card)
async def callback_point(callback: types.CallbackQuery, state: FSMContext):
    """
    A general function for RU and ENG pagination cards.
    """
    async with state.proxy() as data:
        mess = data['card_array']
        len_mess = len(mess)
        cnt = data['count']

        if callback.data in ['app_train_pagination_en_true', 'app_train_pagination_ru_true']:
            data['card_true'].append(mess[cnt - 1])
        elif callback.data in ['app_train_pagination_en_false', 'app_train_pagination_ru_false']:
            data['card_false'].append(mess[cnt - 1])

        card_true = data['card_true']
        card_false = data['card_false']
        len_card_true = len(card_true)
        if cnt == 0:
            correct_answer = 0
        else:
            correct_answer = int((len_card_true/cnt)*100)

        if len(data['card_array']) != data['count']:
            en_callback = ['entoru', 'app_train_pagination_en_true',
                           'app_train_pagination_en_false']
            ru_callback = ['rutoen', 'app_train_pagination_ru_true',
                           'app_train_pagination_ru_false']
            if callback.data in en_callback:
                hidden_text = hspoiler(f'{mess[cnt][2]}')
                await callback.message.answer(
                    text=f'{cnt+1}/{len_mess} (#{mess[cnt][0]})\n\n'
                    f'{mess[cnt][1]}\n\n{hidden_text}\n\n'
                    f'🔴 {len(card_false)} - {len(card_true)} 🟢'
                    f' ({correct_answer}%)',
                    reply_markup=kb_train_pagination_en
                )
                await callback.message.delete()
                data['count'] += 1
            elif callback.data in ru_callback:
                hidden_text = hspoiler(f'{mess[cnt][1]}')
                await callback.message.answer(
                    text=f'{cnt+1}/{len_mess} (#{mess[cnt][0]})\n\n'
                    f'{mess[cnt][2]}\n\n{hidden_text}\n\n'
                    f'🔴 {len(card_false)} - {len(card_true)} 🟢'
                    f' ({correct_answer}%)',
                    reply_markup=kb_train_pagination_ru
                )
                await callback.message.delete()
                data['count'] += 1

        else:
            card_false_string = ''
            user_id = callback.from_user.id
            query = cursor.execute('''
                            SELECT favourites_word.id_word, users.tg_id 
                            FROM favourites_word 
                            INNER JOIN users
                            ON favourites_word.user_id = users.id;'''
                                   ).fetchall()
            id_user_id = cursor.execute(
                f'''SELECT id FROM users WHERE tg_id = {user_id}''').fetchone()
            connection.commit()
            for phrase in data['card_false']:
                card_false_string += f'#{phrase[0]}: {phrase[1]} - {phrase[2]}\n'
            await callback.message.edit_text(
                text=f"Фразы которые стоит повторить\n{card_false_string}",
                reply_markup=kb_main_menu
            )
            for k in data['card_false']:
                for i, j in query:
                    if k[0] == i and user_id == j:
                        data['card_false'].remove(k)

            for i in data['card_false']:
                cursor.execute(
                    f"""INSERT INTO favourites_word(id_word, user_id) VALUES ('{i[0]}', '{id_user_id[0]}');""")
                connection.commit()
            await state.finish()


@dp.message_handler(state=FSMChoiceThemeAll.theme)
async def get_cards(message: types.Message, state: FSMContext):
    """
    Function for getting all cards without pagination
    """
    if message.text.isdigit():
        id = message.text
        query = cursor.execute(f"SELECT * FROM words WHERE word_id = {id};")
        connection.commit()
        data = ''
        for i in query:
            data += f'#{i[0]} {i[1]} - {i[2]}\n'
        if len(data) < 4096:
            await message.answer(f'{data}', reply_markup=kb_main_menu)
        else:
            await message.answer(f'Слишком много карточек', reply_markup=kb_main_menu)
        await state.finish()
    else:
        await message.answer(
            text="⚠ Надо ввести положительное число",
            reply_markup=kb_state_exit
        )


@dp.callback_query_handler(lambda c: c.data == 'settings_callback')
async def settings_callback(callback: types.CallbackQuery):
    """
    Function for the general settings menu
    """
    await callback.message.edit_text(text='Здесь вы можете поменять настройки карточек?', reply_markup=kb_select_settings)

# Code block for Add theme in Settings


@dp.callback_query_handler(lambda c: c.data == 'setting_add_theme')
async def settings_add_theme(callback: types.CallbackQuery):
    """
    The function that triggers the state for Add Theme
    """
    await callback.message.answer(
        text='Введите описание темы\n\nПример: Present Simple Do and Does Questions',
        reply_markup=kb_state_exit
    )
    await FSMSettingAddTheme.titile.set()


@dp.message_handler(state=FSMSettingAddTheme.titile)
async def state_add_theme_title(message: types.Message, state: FSMContext):
    """
    The function for catch State Add Theme
    """
    async with state.proxy() as data:
        data['title'] = message.text
    await message.answer(
        text='Введите номер или номера уроков\n\nПример: "33" или "34-45"',
        reply_markup=kb_state_exit
    )
    await FSMSettingAddTheme.next()


@dp.message_handler(state=FSMSettingAddTheme.lesson)
async def state_add_theme_lesson(message: types.Message, state: FSMContext):
    """
    The function for catch State Add Theme and insert query into Data Base
    """
    async with state.proxy() as data:
        lesson = message.text
        title = data['title']
        cursor.execute(
            f"""INSERT INTO words_info(title, lesson) VALUES ('{title}', '{lesson}');""")
        connection.commit()
    await state.finish()
    await message.answer(
        text='Хотите еще добавить тему?',
        reply_markup=kb_settings_repeat_theme
    )

# Code block for Add card in Settings


@dp.message_handler(state=FSMSettingAddCard.choice_theme)
async def state_add_card(message: types.Message, state: FSMContext):
    """
    The function that triggers the state for Add Card
    """
    if message.text.isdigit():
        await state.finish()
        id = message.text
        await FSMSettingAddCardItems.word_en.set()
        async with state.proxy() as data:
            data['id'] = id
        await message.answer(
            text='🇺🇸 Введите Английскую сторону карточки',
            reply_markup=kb_state_exit
        )
    else:
        await message.answer(
            text="⚠ Надо ввести положительное число",
            reply_markup=kb_state_exit
        )


@dp.message_handler(state=FSMSettingAddCardItems.word_en)
async def state_add_card_en(message: types.Message, state: FSMContext):
    """
    The function for catch State Add Card
    """
    async with state.proxy() as data:
        data['word_en'] = message.text
    await FSMSettingAddCardItems.next()
    await message.answer(
        text='🇷🇺 Введите Русскую сторону карточки',
        reply_markup=kb_state_exit
    )


@dp.message_handler(state=FSMSettingAddCardItems.word_ru)
async def state_add_card_ru(message: types.Message, state: FSMContext):
    """
    The function for catch State Add Card and insert query into Data Base
    """
    async with state.proxy() as data:
        rus = message.text
        eng = data['word_en']
        id = data['id']
        cursor.execute(
            f"""INSERT INTO words(word_en, word_ru, word_id) VALUES ("{eng}", "{rus}", {id});""")
        connection.commit()
    await state.finish()
    await message.answer(
        text='Хотите еще добавить карточку?',
        reply_markup=kb_settings_repeat_card
    )

# Code block for Change theme in Settings


@dp.message_handler(state=FSMSettingChangeTheme.id_theme)
async def change_theme_id(message: types.Message, state: FSMContext):
    """
    The function that triggers the state for Change Theme
    """
    if message.text.isdigit():
        async with state.proxy() as data:
            data['id'] = message.text
        await message.answer(
            text='Введите новое название для темы',
            reply_markup=kb_state_exit
        )
        await FSMSettingChangeTheme.title_word.set()
    else:
        await message.answer(
            text="⚠ Надо ввести положительное число",
            reply_markup=kb_state_exit
        )


@dp.message_handler(state=FSMSettingChangeTheme.title_word)
async def change_theme_id(message: types.Message, state: FSMContext):
    """
    The function for catch State Change Theme
    """
    async with state.proxy() as data:
        data['title_word'] = message.text
    await message.answer(
        text='Введите новый номер урока',
        reply_markup=kb_state_exit
    )
    await FSMSettingChangeTheme.lesson.set()


@dp.message_handler(state=FSMSettingChangeTheme.lesson)
async def change_theme_id(message: types.Message, state: FSMContext):
    """
    The function for catch State Change Theme and insert query into Data Base
    """
    async with state.proxy() as data:
        id_word = data['id']
        title = data['title_word']
        lesson = message.text
        cursor.execute(
            f"""UPDATE words_info SET title = '{title}', lesson = '{lesson}' WHERE id = {id_word}""")
        connection.commit()
    await message.answer(
        text='Еще что-нибудь будем менять?',
        reply_markup=kb_settings_change_theme
    )
    await state.finish()

# Code block for Change card in Settings


@dp.callback_query_handler(lambda c: c.data == 'setting_change_card')
async def change_word_id(callback: types.CallbackQuery):
    """
    The function that triggers the state for Change Card
    """
    await FSMSettingChangeCard.id_card.set()
    await callback.message.answer(
        text='🆔 Введите ID карточки',
        reply_markup=kb_state_exit
    )


@dp.message_handler(state=FSMSettingChangeCard.id_card)
async def change_word_en(message: types.Message, state: FSMContext):
    """
    The function for catch State Change Card
    """
    async with state.proxy() as data:
        data['id_word'] = message.text
    await FSMSettingChangeCard.word_en.set()
    await message.answer(
        text='🇺🇸 Введите Английскую сторону карточки, которую нужно изменить',
        reply_markup=kb_state_exit
    )


@dp.message_handler(state=FSMSettingChangeCard.word_en)
async def change_word_ru(message: types.Message, state: FSMContext):
    """
    The function for catch State Change Card
    """
    async with state.proxy() as data:
        data['en_word'] = message.text
    await FSMSettingChangeCard.word_ru.set()
    await message.answer(
        text='🇷🇺 Введите Русскую сторону карточки, которую нужно изменить',
        reply_markup=kb_state_exit
    )


@dp.message_handler(state=FSMSettingChangeCard.word_ru)
async def change_word_ru(message: types.Message, state: FSMContext):
    """
    The function for catch State Change Card and insert query into Data Base
    """
    async with state.proxy() as data:
        id_word = data['id_word']
        ru_word = message.text
        en_word = data['en_word']
        cursor.execute(f"""
            UPDATE 
                words 
            SET 
                word_en = '{en_word}', 
                word_ru = '{ru_word}' 
            WHERE 
                id = {id_word}
            """)
        connection.commit()
    await state.finish()
    await message.answer(
        text='Еще что-нибудь будем менять?',
        reply_markup=kb_settings_change_card
    )

# General function for all noname state


@dp.callback_query_handler(state='*')
async def cancel_state(callback: types.CallbackQuery, state: FSMContext):
    """
    A function that catches the state without a callback
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.edit_text(
        text='Что будем делать дальше?',
        reply_markup=kb_main_menu
    )

# Final settings


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Вывести справку"),
        ]
    )


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "The Bot starting...")

        except Exception as err:
            logging.exception(err)


async def on_startup(dispatcher):
    # Set default command
    await set_default_commands(dispatcher)

    # Notification about start
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
