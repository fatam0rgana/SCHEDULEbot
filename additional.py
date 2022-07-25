from crontab import CronTab
from datetime import datetime


def create_job(event, chat_id, text, time):
    my_cron = CronTab(user='pazon')
    command_at = 'python3 /home/pazon/SCHEDULEbot/sender.py {0!s} \'{1!s}\''.format(chat_id, text)
    print(command_at)
    job = my_cron.new(command=command_at, comment=f'{event}{chat_id}')
    job.enable()
    job.setall(datetime(2022, time[3], time[2], time[1], time[0]))
    my_cron.write()


def set_up_notification(chat_id, eventname, eventtime, timezone):
    text_to_send = eventname + " starts in 1 hour!"
    eventtime = eventtime.replace(':', ' ').replace('-', ' ').split()
    int_eventtime = list(map(lambda x: int(x), eventtime))
    if int_eventtime[-3] >= 1 - timezone:
        int_eventtime[-3] -= 1 + timezone
    else:
        int_eventtime[-3] += 23 - timezone
        int_eventtime[-4] -= 1
    notification_time = [x for x in int_eventtime[-2:0:-1]]
    create_job(event=eventname,
               chat_id=chat_id,
               text=text_to_send,
               time=notification_time
               )
    print(notification_time)


def delete_notification(eventname, user_id):
    cron = CronTab(user="pazon")
    cron.remove_all(comment=f'{eventname}{user_id}')
    cron.write()


def create_deletion(event, chat_id, time):
    my_cron = CronTab(user='pazon')
    my_cron1 = CronTab(user='pazon')
    command_at = 'python3 /home/pazon/SCHEDULEbot/deleter.py \'{0!s}\' {1!s}'.format(event, chat_id)
    job = my_cron.new(command=command_at, comment=f'{event}{chat_id}')
    job.enable()
    job.setall(datetime(2022, time[3], time[2], time[1], time[0]))
    my_cron.write()


def delete_job_in_time(event, chat_id, time, timezone):
    time = time.replace(':', ' ').replace('-', ' ').split()
    int_eventtime = list(map(lambda x: int(x), time))
    if int_eventtime[-3] >= timezone:
        int_eventtime[-3] -= timezone
    else:
        int_eventtime[-3] += 24 - timezone
        int_eventtime[-4] -= 1
    deletion_time = [x for x in int_eventtime[-2:0:-1]]
    create_deletion(event, chat_id, deletion_time)
