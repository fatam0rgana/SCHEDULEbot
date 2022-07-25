import datetime

from sqlite3 import IntegrityError

from aiogram.types import Message, CallbackQuery, Chat

from app import bot, dp
from callback import tz_callback
from config import admin_id
from database import sql_start, add_record, get_all_records_by_userid, del_record, edit_record, user_exists, \
    add_users, change_timezone_in_db, get_utc, create_db
from fsm import FSMAddEvent, FSMEditEvent
from keyboards import kb_start, kb_cancel, kb_sc, choice_tz
from additional import set_up_notification, delete_notification, delete_job_in_time

prev_msg = ''
eventName = ''
event_index = 0


async def on_startup(dp):
    await bot.send_message(chat_id=admin_id, text='Bot is on')
    create_db()
    sql_start()


@dp.message_handler(commands=['start', 'help'])
async def start_bot(message: Message):
    try:
        if not user_exists(message.from_user.id):
            await add_users(message.from_user.id)
        await bot.send_message(message.from_user.id, "Hello! This is schedule bot. Your default timezone is UTC +3. \n"
                                                     "If you want to change it, select '/change_timezone' in menu "
                                                     "below.",
                               reply_markup=kb_start)
    except:
        await message.reply('You have to start bot first.')


@dp.message_handler(commands=['change_timezone'])
async def edit_tz(message: Message):
    try:
        await message.reply(text='Change timezone:', reply_markup=choice_tz)

    except:
        await message.reply('You have to start bot first.')


@dp.callback_query_handler(tz_callback.filter(zone_format='utc'))
async def choose_timezone(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    await change_timezone_in_db(call.from_user.id, callback_data.get('number'))
    for elem in get_all_records_by_userid(call.from_user.id)[1]:
        delete_notification(elem[0], call.from_user.id)
        set_up_notification(call.from_user.id, elem[0], elem[1], int(callback_data.get('number')))
    await call.message.answer(f"You have chosen UTC {callback_data.get('text_to_display')}",
                              reply_markup=kb_start)


@dp.message_handler(commands=['add_event'], state=None)
async def add_event(message: Message):
    try:
        await FSMAddEvent.event_name.set()
        await message.reply('Enter event name:', reply_markup=kb_cancel)
    except:
        await message.reply('You have to start bot first.')


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: Message, state: FSMAddEvent):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=kb_start)


@dp.message_handler(state=FSMAddEvent.event_name)
async def add_name(message: Message, state: FSMAddEvent):
    async with state.proxy() as data:
        data['event_name'] = str(message.text)
    await FSMAddEvent.next()
    await message.reply('Enter time when the event begins (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)


@dp.message_handler(state=FSMAddEvent.event_begins)
async def add_beginning(message: Message, state: FSMAddEvent):
    async with state.proxy() as data:
        try:
            datetime.datetime.strptime(message.text + ':00', '%Y-%m-%d %H:%M:%S')
            data['event_start'] = message.text + ':00'
            await FSMAddEvent.next()
            await message.reply('Enter time when the event ends (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)
        except:
            await message.reply('Invalid format of date/time \n'
                                'Enter time when the event begins (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)
            await FSMAddEvent.event_begins.set()


@dp.message_handler(state=FSMAddEvent.event_ends)
async def add_end(message: Message, state: FSMAddEvent):
    try:
        async with state.proxy() as data:
            datetime.datetime.strptime(message.text + ':00', '%Y-%m-%d %H:%M:%S')
            data['event_end'] = message.text + ':00'
            data['user_id'] = message.from_user.id
        await add_record(state)
        await message.reply(f"{data['event_name']} added", reply_markup=kb_start)
        set_up_notification(message.from_user.id, data['event_name'], data['event_start'], int(get_utc(message.from_user.id)))
        delete_job_in_time(data['event_name'], message.from_user.id, data['event_start'], int(get_utc(message.from_user.id)))
        await state.finish()
    except IntegrityError as I:
        await message.answer('Event with same name exists.\n'
                             'Try add operation again \n'
                             'Enter event name:', reply_markup=kb_cancel)
        await FSMAddEvent.event_name.set()
    except ValueError as V:
        await message.reply('Invalid format of date/time \n'
                            'Enter time when the event ends (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)
        await FSMAddEvent.event_ends.set()


@dp.message_handler(commands='get_schedule')
async def get_schedule(message: Message):
    printed_res = f'All events for user {message.from_user.first_name} {message.from_user.last_name}: \n \
{get_all_records_by_userid(message.from_user.id)[0]}'
    await message.reply(printed_res, reply_markup=kb_start)
    return printed_res


@dp.message_handler(commands=['delete_event', 'edit_event'])
async def delete_event(message: Message, state=None):
    try:
        await FSMEditEvent.begin.set()
        if len(get_all_records_by_userid(message.from_user.id)[1]) < 1:
            current_state = await state.get_state()
            if current_state is None:
                return
            await state.finish()
            await message.reply('You have no events.', reply_markup=kb_start)
        else:
            global prev_msg
            prev_msg = message.text
            if prev_msg == '/delete_event':
                await message.reply(
                    f'Select index of event you want to delete.\n {get_all_records_by_userid(message.from_user.id)[0]}',
                    reply_markup=kb_cancel)
            else:
                await message.reply(
                    f'Select index of event you want to edit.\n {get_all_records_by_userid(message.from_user.id)[0]}')
            await FSMEditEvent.choose_ind.set()
    except:
        await message.reply('You have to start bot first.')


@dp.message_handler(state=FSMEditEvent.choose_ind)
async def choose_index(message: Message, state=FSMEditEvent):
    try:
        if int(message.text) < 1:
            raise Exception
        global event_index
        event_index = int(message.text) - 1
        if prev_msg == '/delete_event':
            await FSMEditEvent.delete.set()
            await message.reply(f'{get_all_records_by_userid(message.from_user.id)[1][int(message.text) - 1][0]} deleted.',
                                reply_markup=kb_start)
            delete_notification(get_all_records_by_userid(message.from_user.id)[1][int(message.text) - 1][0], message.from_user.id)
            await del_record(message.from_user.id,
                             get_all_records_by_userid(message.from_user.id)[1][int(message.text) - 1][0])
            await state.finish()
        else:
            await FSMEditEvent.edit_name.set()
            global eventName
            eventName = get_all_records_by_userid(message.from_user.id)[1][int(message.text) - 1][0]
            await message.reply('Enter event name:', reply_markup=kb_sc)
    except:
        await message.reply('You entered invalid data. It must be index of an event shown in previous message.',
                            reply_markup=kb_cancel)
        await FSMEditEvent.choose_ind.set()


@dp.message_handler(state=FSMEditEvent.edit_name)
async def edit_name(message: Message, state=FSMEditEvent):
    async with state.proxy() as data:
        if message.text == '/skip':
            data['event_name'] = get_all_records_by_userid(message.from_user.id)[1][event_index][0]
        else:
            data['event_name'] = str(message.text)
    await FSMEditEvent.next()
    await message.reply('Enter time when the event begins:', reply_markup=kb_sc)


@dp.message_handler(state=FSMEditEvent.edit_tb)
async def edit_tb(message: Message, state=FSMEditEvent):
    try:
        async with state.proxy() as data:
            if message.text == '/skip':
                data['event_begins'] = get_all_records_by_userid(message.from_user.id)[1][event_index][1]
            else:
                datetime.datetime.strptime(message.text + ':00', '%Y-%m-%d %H:%M:%S')
                data['event_begins'] = message.text + ':00'
        await FSMEditEvent.next()
        await message.reply('Enter time when the event ends:', reply_markup=kb_sc)
    except:
        await message.reply('Invalid format of date/time \n'
                            'Enter time when the event begins (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)
        await FSMEditEvent.edit_tb.set()


@dp.message_handler(state=FSMEditEvent.edit_te)
async def edit_te(message: Message, state=FSMEditEvent):
    try:
        async with state.proxy() as data:
            if message.text == '/skip':
                data['event_ends'] = get_all_records_by_userid(message.from_user.id)[1][event_index][2]
            else:
                datetime.datetime.strptime(message.text + ':00', '%Y-%m-%d %H:%M:%S')
                data['event_ends'] = message.text
            data['user_id'] = message.from_user.id
        await edit_record(state, message.from_user.id, eventName)
        delete_notification(get_all_records_by_userid(message.from_user.id)[1][event_index][0], message.from_user.id)
        set_up_notification(message.from_user.id, data['event_name'], data['event_begins'], int(get_utc(message.from_user.id)))
        await message.reply(f"{data['event_name']} edited", reply_markup=kb_start)
        await state.finish()
    except IntegrityError as I:
        print('1')
        await message.answer('Event with same name exists.\n'
                             'Try edit operation again \n'
                             f'{get_all_records_by_userid(message.from_user.id)[0]}', reply_markup=kb_cancel)
        await FSMEditEvent.choose_ind.set()
    except ValueError as V:
        await message.reply('Invalid format of date/time \n'
                            'Enter time when the event ends (YYYY-MM-DD hh:mm):', reply_markup=kb_cancel)
        await FSMEditEvent.edit_te.set()
