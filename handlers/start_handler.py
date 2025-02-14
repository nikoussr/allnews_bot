from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
import time

import configs
import keyboards.keyboard
from backend import backend
from backend.backend import get_all_news
from states.states import States
from database.db import set_themes, get_themes, del_theme, user_exists, create_new_user, change_active
from keyboards.keyboard import all_themes, exit_btn
from main import bot

router = Router()

from main import db
@router.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id,
                                            reply_markup=None)
    except TelegramBadRequest:
        pass

    # если пользователь новый
    if not (await user_exists(db, user_id)):
        a = message.date
        b = str(a.date()) + " " + str(a.time())
        await create_new_user(db=db, user_id=user_id, active=True, date=b, first_name=message.from_user.first_name,
                              last_name=message.from_user.last_name, nickname=message.from_user.username)
        await message.answer(f"Привет {message.from_user.username}. Это бот для ленты новостей.")
        time.sleep(1)
        await message.answer(
            f"Давайте добавим новые темы в Вашу ленту новостей! Нажимайте на кнопку, если вас это интересует.\nЕсли вы выбрали свои темы, то нажмите 'Продолжить'",
            reply_markup=keyboards.keyboard.all_themes(configs.themes, 'continue'))
        await state.set_state(States.wait_for_themes)
    # если пользователь старый
    else:
        await message.answer(f"Привет, как дела? Тут скоро будет отвечать нейросеть, если ты уже проходил этот этап")


@router.callback_query(States.wait_for_themes)
async def add_themes(callback: CallbackQuery, state: FSMContext):
    selected_theme = callback.data
    data = await state.get_data()
    themes = data.get('selected_themes', [])
    user_id = callback.from_user.id
    print(f"{user_id} выбирает темы в первый раз")
    if selected_theme == 'continue':
        try:
            # Вставляем выбранные темы в базу данных
            await set_themes(db, user_id, themes)
            await callback.answer("Темы успешно сохранены!")
            await callback.message.edit_text(f"Отлично! Если хотите получить свежие новости, то используйте команду /news", reply_markup=None)
        except Exception as e:
            print(f"Ошибка при сохранении тем: {e}")
            await callback.answer("Произошла ошибка при сохранении тем.")
    else:
        if selected_theme not in themes:
            themes.append(selected_theme)

        await state.update_data(selected_themes=themes)

        themes_text = "\n".join(theme for theme in themes)

        await callback.message.edit_text(
            f"Вы выбрали темы:\n{themes_text}",
            reply_markup=keyboards.keyboard.update_themes_btn_generator('continue', themes)
        )

        await state.set_state(States.wait_for_themes)


@router.message(Command('themes'))
async def command_themes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    print(f"{user_id} хочет посмотреть свои темы")
    themes = await get_themes(db=db, user_id=user_id)
    if not themes:
        await message.answer(f"У вас еще нет тем.")
        await state.clear()
        return
    kb = all_themes(themes, 'exit')
    try:
        await message.answer(f"Ваши темы. Если хочешь удалить что-то - нажми на нужную кнопку.", reply_markup=kb)
    except:
        await message.answer(f"Вы еще не выбрали ни одну тему.")
    finally:
        await state.set_state(States.wait_for_deleting_theme)


@router.callback_query(States.wait_for_deleting_theme)
async def del_themes(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'exit':
        await callback.answer(f"Успешно")
        await callback.message.delete(inline_message_id=callback.inline_message_id)
        await state.clear()
    else:
        user_id = callback.from_user.id
        print(f"{user_id} удаляет свои темы")
        await del_theme(db=db, user_id=user_id, theme=callback.data)

        # Получаем обновленный список тем
        themes = await get_themes(db=db, user_id=user_id)

        if not themes:  # Проверяем, если темы отсутствуют
            await callback.message.edit_text("Все темы удалены.")
        else:
            kb = all_themes(themes, 'exit')
            await callback.message.edit_text(
                "Ваши темы. Если хочешь удалить что-то - нажми на нужную кнопку.",
                reply_markup=kb
            )

        await state.set_state(States.wait_for_deleting_theme)


@router.message(Command('add'))
async def command_add(message: Message, state: FSMContext):
    user_id = message.from_user.id
    print(f"{user_id} хочет добавить новые темы")
    try:
        # Извлекаем текущие темы пользователя
        user_themes = await db.fetch('SELECT theme FROM themes WHERE user_id = $1', user_id)
        user_themes_set = {record['theme'] for record in user_themes}
        # Получаем все доступные темы из вашего модуля с темами
        all_themes = set(configs.themes)  # configs.themes теперь массив
        # Определяем темы, которых нет у пользователя
        available_themes = all_themes - user_themes_set

        if not available_themes:
            await message.answer("У вас уже есть все доступные темы!")
            return

        await message.answer("Выберите тему для добавления:",
                             reply_markup=keyboards.keyboard.update_themes_btn_generator('continue', user_themes_set))

        # Сохраняем состояние, чтобы знать, что пользователь выбирает тему
        await state.set_state(States.wait_for_add_theme)
    except Exception as e:
        print(f"Ошибка при получении тем: {e}")
        await message.answer("Произошла ошибка при получении тем.")


@router.callback_query(States.wait_for_add_theme)
async def add_new_theme(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_theme = callback.data
    print(f"{user_id} добавил {selected_theme}")

    if selected_theme != 'continue':
        try:
            # Добавляем выбранную тему в базу данных
            await db.execute('INSERT INTO themes(user_id, theme) VALUES($1, $2)', user_id, selected_theme)
            await callback.answer(f"Тема '{selected_theme}' успешно добавлена!")  # configs.themes больше не нужен
        except Exception as e:
            print(f"Ошибка при добавлении темы: {e}")
            await callback.answer("Произошла ошибка при добавлении темы.")

        user_themes = await db.fetch('SELECT theme FROM themes WHERE user_id = $1', user_id)
        user_themes_set = {record['theme'] for record in user_themes}

        await callback.message.edit_text(f"Выберите тему для добавления:",
                                         reply_markup=keyboards.keyboard.update_themes_btn_generator('continue',
                                                                                                     user_themes_set))
        await state.set_state(States.wait_for_add_theme)
    else:
        await callback.answer("Успешно")
        await callback.message.delete(inline_message_id=callback.inline_message_id)
        await state.clear()


@router.message(Command('suggest'))
async def command_suggest(message: Message, state: FSMContext):
    await message.answer(
        "Здравствуйте! Если у вас есть какие-либо вопросы, предложения или Вы нашли баги, пожалуйста, напишите мне.\nЯ всегда готов помочь и выслушать Ваше мнение. Спасибо!",
        reply_markup=exit_btn)
    await state.set_state(States.wait_for_suggest)

@router.message(Command('news'))
async def news(message: Message):
    await message.answer("Собираю новости... Пожалуйста, подожди немного.")
    themes = await get_themes(db=db, user_id=message.from_user.id)
    news_list = await get_all_news()
    count = 0
    for news in news_list:
        title = news["title"]
        link = news["link"]
        source = news["source"]
        prompt = f"Определи, к какой из категорий относится новость. Затем создай краткую выжимку:\nЗаголовок: {title}\nСсылка: {link}"
        summary = await backend.generate_summary(prompt)
        summaries = {}
        summaries.update ({"summary": summary, "source": source, "link": link})
        for i in themes:
            if i in summary:
                count += 1
                await message.answer(
                    f"{summaries['summary']}\nИсточник: {summaries['source']}\nСсылка: {summaries['link']}"
                )
    if count == 0:
        await message.answer(f'Свежих новостей по твоим интересам пока нет, попробуй позже')


@router.message(States.wait_for_suggest)
async def suggest_text(message: Message, state: FSMContext):
    from main import bot
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await message.answer(f"Cообщение доставлено")
    await bot.send_message(695088267, f"Сообщение от {message.from_user.full_name}:\n{message.text}")
    await state.clear()


@router.callback_query()
async def exit_continue(callback: CallbackQuery, state: FSMContext):
    if callback.data in ['exit', 'continue']:
        await callback.message.delete(inline_message_id=callback.inline_message_id)
        await callback.answer(f"Успешно")
        await state.clear()


@router.my_chat_member()
async def my_chat_member(message: ChatMemberUpdated):
    """Проверка на бан бота. Редактирует столбец active"""
    if message.chat.type == 'private':
        if message.new_chat_member.status == 'kicked':
            await change_active(db, message.from_user.id, False)
        elif message.new_chat_member.status == 'member':
            await message.answer("Давно не виделись!")
            await change_active(db, message.from_user.id, True)
