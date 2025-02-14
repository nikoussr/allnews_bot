from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import configs

exit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')]
                                                 ])


def all_themes(themes, state):
    all_themes = []
    themes_count = 0
    while themes_count < len(themes):
        if len(themes) - themes_count >= 2:
            all_themes.append([InlineKeyboardButton(text=themes[themes_count], callback_data=themes[themes_count]),
                               InlineKeyboardButton(text=themes[themes_count + 1],
                                                    callback_data=themes[themes_count + 1])])
            themes_count += 2
        else:
            all_themes.append([InlineKeyboardButton(text=themes[themes_count], callback_data=themes[themes_count])])
            themes_count += 1
    if state == 'exit':
        all_themes.append([InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')])
    elif state == 'continue':
        all_themes.append([InlineKeyboardButton(text='Продолжить ⏭', callback_data='continue')])
    return InlineKeyboardMarkup(inline_keyboard=all_themes)


def update_themes_btn_generator(state, themes_to_del):
    themes = [theme for theme in configs.themes if theme not in themes_to_del]

    all_themes = []
    themes_count = 0

    while themes_count < len(themes):
        if len(themes) - themes_count >= 2:
            all_themes.append([InlineKeyboardButton(text=themes[themes_count], callback_data=themes[themes_count]),
                               InlineKeyboardButton(text=themes[themes_count + 1],
                                                    callback_data=themes[themes_count + 1])])
            themes_count += 2
        else:
            all_themes.append([
                InlineKeyboardButton(
                    text=themes[themes_count],
                    callback_data=themes[themes_count]
                )
            ])
            themes_count += 1

    if state == 'exit':
        all_themes.append([InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')])
    elif state == 'continue':
        all_themes.append([InlineKeyboardButton(text='Продолжить ⏭', callback_data='continue')])
    return InlineKeyboardMarkup(inline_keyboard=all_themes)
