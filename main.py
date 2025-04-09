import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from database import TaskDatabase

# Database setup
db = TaskDatabase()

# Bot states
ADD_DESCRIPTION, ADD_PRIORITY, EDIT_TASK, EDIT_DESCRIPTION, EDIT_PRIORITY = range(5)

# Priority mapping
PRIORITIES = {
    1: "🔵 Low",
    2: "🟡 Medium",
    3: "🔴 High"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Task Manager Bot!\n\n"
        "Available commands:\n"
        "/add - Add a new task\n"
        "/list - Show all tasks\n"
        "/edit - Edit a task\n"
        "/delete - Delete a task\n"
        "/help - Show this help message"
    )

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = db.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("You have no tasks yet!")
        return
    
    message = "Your tasks:\n\n"
    for task in tasks:
        message += f"{task.id}. {task.description} - {PRIORITIES.get(task.priority, 'Unknown')}\n"
    
    await update.message.reply_text(message)

async def add_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the task description:")
    return ADD_DESCRIPTION

async def add_task_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Low", callback_data="1")],
        [InlineKeyboardButton("Medium", callback_data="2")],
        [InlineKeyboardButton("High", callback_data="3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select task priority:",
        reply_markup=reply_markup
    )
    return ADD_PRIORITY

async def add_task_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    priority = int(query.data)
    description = context.user_data['description']
    user_id = query.from_user.id
    
    db.add_task(user_id, description, priority)
    await query.edit_message_text(f"Task added: {description} - {PRIORITIES.get(priority, 'Unknown')}")
    
    return ConversationHandler.END

async def edit_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = db.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("You have no tasks to edit!")
        return ConversationHandler.END
    
    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(
            f"{task.id}. {task.description} - {PRIORITIES.get(task.priority, 'Unknown')}",
            callback_data=f"edit_{task.id}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select task to edit:",
        reply_markup=reply_markup
    )
    
    return EDIT_TASK

async def edit_task_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    task_id = int(query.data.split('_')[1])
    context.user_data['task_id'] = task_id
    
    keyboard = [
        [InlineKeyboardButton("Edit Description", callback_data="description")],
        [InlineKeyboardButton("Edit Priority", callback_data="priority")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "What do you want to edit?",
        reply_markup=reply_markup
    )
    
    return EDIT_TASK

async def edit_task_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    context.user_data['edit_choice'] = choice
    
    if choice == "description":
        await query.edit_message_text("Please enter the new description:")
        return EDIT_DESCRIPTION
    else:
        keyboard = [
            [InlineKeyboardButton("Low", callback_data="1")],
            [InlineKeyboardButton("Medium", callback_data="2")],
            [InlineKeyboardButton("High", callback_data="3")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select new priority:",
            reply_markup=reply_markup
        )
        return EDIT_PRIORITY

async def edit_task_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_description = update.message.text
    task_id = context.user_data['task_id']
    user_id = update.effective_user.id
    
    success = db.edit_task(user_id, task_id, description=new_description)
    
    if success:
        await update.message.reply_text("Task description updated successfully!")
    else:
        await update.message.reply_text("Failed to update task description.")
    
    return ConversationHandler.END

async def edit_task_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    new_priority = int(query.data)
    task_id = context.user_data['task_id']
    user_id = query.from_user.id
    
    success = db.edit_task(user_id, task_id, priority=new_priority)
    
    if success:
        await query.edit_message_text(f"Task priority updated to {PRIORITIES.get(new_priority, 'Unknown')}!")
    else:
        await query.edit_message_text("Failed to update task priority.")
    
    return ConversationHandler.END

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = db.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("You have no tasks to delete!")
        return
    
    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(
            f"{task.id}. {task.description} - {PRIORITIES.get(task.priority, 'Unknown')}",
            callback_data=f"delete_{task.id}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select task to delete:",
        reply_markup=reply_markup
    )

async def delete_task_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    task_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    success = db.delete_task(user_id, task_id)
    
    if success:
        await query.edit_message_text("Task deleted successfully!")
    else:
        await query.edit_message_text("Failed to delete task.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN environment variable set")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("delete", delete_task))
    application.add_handler(CallbackQueryHandler(delete_task_confirm, pattern="^delete_"))
    
    # Add task conversation handler
    add_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_task_start)],
        states={
            ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_description)],
            ADD_PRIORITY: [CallbackQueryHandler(add_task_priority)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(add_handler)
    
    # Edit task conversation handler
    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_task_start)],
        states={
            EDIT_TASK: [CallbackQueryHandler(edit_task_select, pattern="^edit_"),
                       CallbackQueryHandler(edit_task_choice, pattern="^(description|priority)$")],
            EDIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_task_description)],
            EDIT_PRIORITY: [CallbackQueryHandler(edit_task_priority)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(edit_handler)
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
