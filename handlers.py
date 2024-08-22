from aiogram import types
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from quiz_data import quiz_data  

router = Router()  # Создаем объект router

# Словарь для хранения текущих индексов вопросов для пользователей
user_quiz_indices = {}
user_scores = {}  # Словарь для хранения счетов игроков

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в квиз! Нажмите кнопку ниже, чтобы начать.",
        reply_markup=InlineKeyboardBuilder().add(
            types.InlineKeyboardButton(text="Начать квиз", callback_data="start_quiz")
        ).as_markup()
    )

@router.callback_query(lambda c: c.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery):
    user_quiz_indices[callback.from_user.id] = 0  # Устанавливаем стартовый индекс
    user_scores[callback.from_user.id] = {"correct": 0, "wrong": 0}  # Счет правильных и неправильных ответов
    await callback.message.answer("Квиз начинается! Подождите...")
    await get_question(callback.message, callback.from_user.id)

@router.callback_query(lambda c: c.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    user_scores[callback.from_user.id]["correct"] += 1 
    await callback.message.answer("Верно!")
    
    await proceed_to_next_question(callback)

@router.callback_query(lambda c: c.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    user_scores[callback.from_user.id]["wrong"] += 1  # Увеличиваем счетчик неправильных ответов
    await callback.message.answer("Неправильно! Переходим к следующему вопросу.")
    
    await proceed_to_next_question(callback)

async def proceed_to_next_question(callback: types.CallbackQuery):
    current_question_index = user_quiz_indices[callback.from_user.id]
    current_question_index += 1
    user_quiz_indices[callback.from_user.id] = current_question_index
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        # Подсчет результатов и вывод на экран
        correct = user_scores[callback.from_user.id]["correct"]
        wrong = user_scores[callback.from_user.id]["wrong"]
        
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен!\n"
            f"Ваш результат: {correct} правильных и {wrong} неправильных ответов."
        )
        
        # Предложим начать квиз заново 
        await callback.message.answer(
            "Хотите пройти квиз снова?",
            reply_markup=InlineKeyboardBuilder().add(
                types.InlineKeyboardButton(text="Начать заново", callback_data="start_quiz")
            ).as_markup()
        )
        del user_quiz_indices[callback.from_user.id]  # Удаляем индекс
        del user_scores[callback.from_user.id]  

async def get_question(message: types.Message, user_id: int):
    """Функция для получения текущего вопроса и отправки его пользователю."""
    current_index = user_quiz_indices[user_id]
    
    if current_index >= len(quiz_data):
        await message.answer("Нет больше вопросов.")
        return
    
    question_data = quiz_data[current_index]
    options = question_data['options']
    keyboard = InlineKeyboardBuilder()
    
    for i, option in enumerate(options):
        callback_data = "right_answer" if i == question_data['correct_option'] else "wrong_answer"
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=callback_data))

    await message.answer(question_data['question'], reply_markup=keyboard.as_markup())  