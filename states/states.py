from aiogram.filters.state import StatesGroup, State


class States(StatesGroup):
    wait_for_themes = State()
    wait_for_comfirm_themes = State()
    wait_for_deleting_theme = State()
    wait_for_suggest = State()
    wait_for_add_theme = State()
    waiting_for_suggestion = State()
