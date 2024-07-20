import sys
import os
import asyncio
import requests
from datetime import datetime, timedelta
# import 

script_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(script_dir, '..'))

from typing import List

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, error
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from telegram.constants import ParseMode




# from app import create_app, db, app
# from app.models import Task, User
from config import Config

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)

def get_user_tasks(user_id):
    response = requests.get(f"http://127.0.0.1:5000/api/tasks/{user_id}")
    return response.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg = update.effective_user
    data = {"tg_id": user_tg.id, "username": user_tg.username}
    response = requests.post("http://127.0.0.1:5000/api/users", json=data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Этот был создан в качестве пет-проекта трекера задача! Используйте /help чтобы посмотреть список доступных команд.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/tasks - Посмотреть все задачи\n"
        "/create - Создать новую задачу\n"
        "/delete - Удалить задачу\n"
        "/edit - Редактировать задачу"
    )

async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg = update.effective_user
    tasks = get_user_tasks(user_tg.id)
    if tasks:
        message = "Ваши задачи:\n"
        for task in tasks:
            message += f"➥ <i><b>{task['title']}</b></i> \nДней до дедлайна: {(datetime.fromisoformat(task['deadline']) - datetime.now()).days + 1}\n\n"
    else:
        message = "У вас нет задач, используйте /create, чтобы создать новую задачу."
    await update.message.reply_text(text=message, parse_mode=ParseMode.HTML)

async def create_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text="Отмена", callback_data="cancel_button")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, введите название задачи:", reply_markup=reply_markup)
    context.user_data['command'] = 'create_task'

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    context.user_data['title'] = title
    await save_task(update, context)
    await edit_task_command(update, context)
    # TODO:
    # Пока так побудет, мб поменяю потом
    return
    

    title = update.message.text
    context.user_data['title'] = title
    await update.message.reply_text("Пожалуйста, введите описание задачи:")
    context.user_data['command'] = 'save_task'

async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = context.user_data['title']
    user_tg = update.effective_user

    data = {"title": title, "tg_id": user_tg.id}
    response = requests.post("http://127.0.0.1:5000/api/task", json=data)

    if response.status_code == 201:
        await update.message.reply_text(f"Задача была добавлена: {title}")
    else:
        await update.message.reply_text(f"Задача не была добавлена.")
    del context.user_data['command']
    del context.user_data['title']

async def edit_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    task_id = context.user_data['task_id']
    field = context.user_data['field']

    user_tg = update.effective_user

    data = {str(field): text}
    response = requests.put(f"http://127.0.0.1:5000/api/task/{task_id}", json=data)
    task_json = response.json()
    task = (
        f"Название: {task_json['title']}\n"
        f"Описание: {task_json['description']}\n"
        f"Дедлайн: {datetime.fromisoformat(task_json['deadline']).strftime('%d.%m')}\n"
        f"Приоритет: {task_json['priority']}\n"
    )

    if response.status_code == 200:
        await update.message.reply_text(f"Задача была обновлена:\n{task}")
    else:
        await update.message.reply_text(f"Задача не была обновлена:\n{task}")
    
        
    del context.user_data['command']
    del context.user_data['task_id']
    del context.user_data['field']

async def edit_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # tasks = Task.query.all()
    user_tg = update.effective_user
    tasks = get_user_tasks(user_tg.id)
    if not tasks:
        await update.message.reply_text("У вас нет задач, используйте /create, чтобы создать новую задачу.")
        return

    keyboard: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"{task['title']}", callback_data=f"edit_task_{task['id']}")]
        for task in tasks
    ]
    keyboard.append([InlineKeyboardButton(text="Отмена", callback_data=f"cancel_button")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите задачу для редактирования:", reply_markup=reply_markup)

async def edit_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split("_")[2])
    response = requests.get(f"http://127.0.0.1:5000/api/task/{task_id}")
    
    if response.status_code == 200:
        task = response.json()
        task_info = (
            f"Название: {task['title']}\n"
            f"Описание: {task['description']}\n"
            f"Дедлайн: {datetime.fromisoformat(task['deadline']).strftime('%d.%m')}\n"
            f"Приоритет: {task['priority']}\n"
            f"Дней потрачено: {task['days_spent']}\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("Изменить название", callback_data=f"edit_title_{task_id}")],
            [InlineKeyboardButton("Изменить описание", callback_data=f"edit_description_{task_id}")],
            [InlineKeyboardButton("Изменить дедлайн", callback_data=f"edit_deadline_{task_id}")],
            [InlineKeyboardButton("Изменить приоритет", callback_data=f"edit_priority_{task_id}")],
            [InlineKeyboardButton("Удалить", callback_data=f"delete_{task_id}")],
            [InlineKeyboardButton("Выполнить", callback_data=f"complete_{task_id}")],
        ]

        keyboard.append([InlineKeyboardButton(text="Отмена", callback_data=f"cancel_button")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(task_info, reply_markup=reply_markup)
        context.user_data['task_id'] = task_id
    else:
        await query.edit_message_text("Задача не найдена.")

async def edit_title_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Пожалуйста, введите новое название задачи:")
    context.user_data['command'] = 'edit_task'
    context.user_data['field'] = 'title'

async def edit_description_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
        
    await query.edit_message_text("Пожалуйста, введите новое описание задачи:")
    context.user_data['command'] = 'edit_task'
    context.user_data['field'] = 'description'

async def edit_deadline_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
        
    
    await query.edit_message_text("Пожалуйста, введите новое количество дней до дедлайна:")
    context.user_data['command'] = 'edit_task'
    context.user_data['field'] = 'deadline'

async def edit_priority_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
        
    await query.edit_message_text("Пожалуйста, введите новый приоритет задачи:")
    context.user_data['command'] = 'edit_task'
    context.user_data['field'] = 'priority'


async def delete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # tasks = Task.query.all()
    user_tg = update.effective_user
    tasks = get_user_tasks(user_tg.id)
    if not tasks:
        await update.message.reply_text("У вас нет задач, используйте /create, чтобы создать новую задачу.")
        return

    keyboard: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"{task['title']}", callback_data=f"delete_{task['id']}")]
        for task in tasks
    ]
    keyboard.append([InlineKeyboardButton(text="Отмена", callback_data=f"cancel_button")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите задачу для удаления:", reply_markup=reply_markup)

async def complete_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = {
        "is_completed":True
    }

    task_id = int(query.data.split("_")[1])
    response = requests.get(f"http://127.0.0.1:5000/api/task/{task_id}")

    task_title = response.json()['title']
    response = requests.delete(f"http://127.0.0.1:5000/api/task/{task_id}", json=data)
    if response.status_code == 204:
        await query.edit_message_text(f"Задача '{task_title}' была успешно выполнена, поздравляю!")
    else:
        await query.edit_message_text("Задача не найдена.")

async def delete_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = {
        "is_completed":False
    }

    task_id = int(query.data.split("_")[1])
    response = requests.get(f"http://127.0.0.1:5000/api/task/{task_id}")

    task_title = response.json()['title']
    response = requests.delete(f"http://127.0.0.1:5000/api/task/{task_id}", json=data)
    if response.status_code == 204:
        await query.edit_message_text(f"Задача '{task_title}' была успешно удалена.")
    else:
        await query.edit_message_text("Задача не найдена.")

async def mark_task_command(tg_id):
    tasks = get_user_tasks(tg_id)

    keyboard = [
        [InlineKeyboardButton(text=f"{task['title']}", callback_data=f"mark_task_{task['id']}_{tg_id}")]
        for task in tasks
    ]
    keyboard.append([InlineKeyboardButton(text="Выбрать/Отмена", callback_data=f"toggle_task")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_message(chat_id=tg_id, text="Если есть, отметьте задачи, которыми Вы сегодня занимались:", reply_markup=reply_markup)

async def mark_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split("_")[-2])
    tg_id = int(query.data.split("_")[-1])
    
    if 'tasks' in context.user_data:
        tasks = context.user_data.get('tasks')
    else:
        tasks = get_user_tasks(tg_id)
        context.user_data['tasks'] = tasks

    task = next(task for task in tasks if task['id'] == task_id)
    
    task['title'] = f"✘ {task['title']}" if '✘' not in task['title'] else task['title'][1:]

    
    keyboard = [
        [InlineKeyboardButton(text=f"{task['title']}", callback_data=f"mark_task_{task['id']}_{tg_id}")]
        for task in tasks
    ]
    keyboard.append([InlineKeyboardButton(text="Выбрать/Отмена", callback_data=f"toggle_task")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Если есть, отметьте задачи, которыми Вы сегодня занимались:", reply_markup=reply_markup)

async def toggle_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tasks = context.user_data.get('tasks', [])
    tasks_counter = 0
    for task in tasks:
        if task['title'][0] != '✘':
            continue
        tasks_counter += 1
        task['days_spent'] += 1
        task['title'] = task['title'][2:]
        response = requests.put(f"http://127.0.0.1:5000/api/task/{task['id']}", json=task)

    if tasks_counter == 0:
        text = "Не расстраивайтесь, следующий день будет более удачным!"
    elif tasks_counter == 1:
        text = f"Отличная работа!\nСегодня Вы продвинулись в {tasks_counter} задаче."
    else:
        text = f"Отличная работа!\nСегодня Вы продвинулись в {tasks_counter} задачах."
    await query.edit_message_text(text)
    
    try:
        del context.user_data['tasks']
    except:
        pass


async def cancel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    print(context.user_data)

    context.user_data.clear()
    await query.edit_message_text("Вы закрыли меню.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'command' in context.user_data:
        command = context.user_data['command']
        if command == 'create_task':
            await get_description(update, context)
        elif command == 'save_task':
            await save_task(update, context)
        elif command == 'edit_task':
            await edit_task(update, context)

async def send_tasks_checkbox(update: Update, context: ContextTypes.DEFAULT_TYPE):

    response = requests.get(f"http://127.0.0.1:5000/api/users")
    data = response.json()
    for user in data:
        try:
            await mark_task_command(user['tg_id'])
        except error.BadRequest as e:
            # TODO:
            # Возможно добавить удаление юзера из БД, если его больше не существует
            pass



async def schedule_daily_task(task, hour, minute):
    while True:
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time < now:
            target_time += timedelta(days=1)
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        await task()

def main():
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('tasks', tasks_command))
    application.add_handler(CommandHandler('create', create_task_command))
    application.add_handler(CommandHandler('delete', delete_task_command))
    application.add_handler(CommandHandler('edit', edit_task_command))
    application.add_handler(CommandHandler('daily', edit_task_command))
    application.add_handler(CommandHandler('test', send_tasks_checkbox))

    application.add_handler(CallbackQueryHandler(delete_task_button, pattern='^delete_'))
    application.add_handler(CallbackQueryHandler(complete_task_button, pattern='^complete_'))
    application.add_handler(CallbackQueryHandler(edit_task_button, pattern='^edit_task_'))
    application.add_handler(CallbackQueryHandler(edit_title_button, pattern='^edit_title_'))
    application.add_handler(CallbackQueryHandler(edit_description_button, pattern='^edit_description_'))
    application.add_handler(CallbackQueryHandler(edit_deadline_button, pattern='^edit_deadline_'))
    application.add_handler(CallbackQueryHandler(edit_priority_button, pattern='^edit_priority_'))
    application.add_handler(CallbackQueryHandler(mark_task_button, pattern='^mark_task_'))
    application.add_handler(CallbackQueryHandler(toggle_task, pattern='^toggle_task'))
    application.add_handler(CallbackQueryHandler(cancel_button, pattern='cancel_button'))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(schedule_daily_task(send_tasks_checkbox, 23, 0))
    application.run_polling()
    
if __name__ == '__main__':
    main()