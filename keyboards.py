from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from callback import tz_callback

choice_tz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='UTC -11', callback_data='tz:utc:-11:-11'),
            InlineKeyboardButton(text='UTC -10', callback_data='tz:utc:-10:-10'),
            InlineKeyboardButton(text='UTC -9', callback_data='tz:utc:-9:-9'),
            InlineKeyboardButton(text='UTC -8', callback_data='tz:utc:-8:-8')
        ],
        [
            InlineKeyboardButton(text='UTC -7', callback_data='tz:utc:-7:-7'),
            InlineKeyboardButton(text='UTC -6', callback_data='tz:utc:-6:-6'),
            InlineKeyboardButton(text='UTC -5', callback_data='tz:utc:-5:-5'),
            InlineKeyboardButton(text='UTC -4', callback_data='tz:utc:-4:-4')
        ],
        [
            InlineKeyboardButton(text='UTC -3', callback_data='tz:utc:-3:-3'),
            InlineKeyboardButton(text='UTC -2', callback_data='tz:utc:-2:-2'),
            InlineKeyboardButton(text='UTC -1', callback_data='tz:utc:-1:-1'),
            InlineKeyboardButton(text='UTC 0', callback_data='tz:utc:0:0')
        ],
        [
            InlineKeyboardButton(text='UTC +1', callback_data='tz:utc:1:+1'),
            InlineKeyboardButton(text='UTC +2', callback_data='tz:utc:2:+2'),
            InlineKeyboardButton(text='UTC +3', callback_data='tz:utc:3:+3'),
            InlineKeyboardButton(text='UTC +4', callback_data='tz:utc:4:+4')
        ],
        [
            InlineKeyboardButton(text='UTC +5', callback_data='tz:utc:5:+5'),
            InlineKeyboardButton(text='UTC +6', callback_data='tz:utc:6:+6'),
            InlineKeyboardButton(text='UTC +7', callback_data='tz:utc:7:+7'),
            InlineKeyboardButton(text='UTC +8', callback_data='tz:utc:8:+8')
        ],
        [
            InlineKeyboardButton(text='UTC +9', callback_data='tz:utc:9:+9'),
            InlineKeyboardButton(text='UTC +10', callback_data='tz:utc:10:+10'),
            InlineKeyboardButton(text='UTC +11', callback_data='tz:utc:11:+11'),
            InlineKeyboardButton(text='UTC +12', callback_data='tz:utc:12:+12')
        ]
    ]
)

help_button = KeyboardButton('/help')
add_button = KeyboardButton('/add_event')
cancel_button = KeyboardButton('/cancel')
get_button = KeyboardButton('/get_schedule')
del_button = KeyboardButton('/delete_event')
edit_button = KeyboardButton('/edit_event')
skip_button = KeyboardButton('/skip')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_sc = ReplyKeyboardMarkup(resize_keyboard=True)

kb_start.add(help_button).add(add_button).add(get_button).add(del_button).add(edit_button)
kb_cancel.add(cancel_button)
kb_sc.add(skip_button).add(cancel_button)
