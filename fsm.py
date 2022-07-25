from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

class FSMAddEvent(StatesGroup):
    event_name = State()
    event_begins = State()
    event_ends = State()

class FSMEditEvent(FSMAddEvent):
    begin = State()
    delete = State()
    choose_ind = State()
    edit_name = State()
    edit_tb = State()
    edit_te = State()
