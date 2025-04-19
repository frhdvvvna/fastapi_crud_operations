from telebot import TeleBot, types

TOKEN = "7922278624:AAFufF5d_BkPumIke7svUJNzY8sehhNR3wY"
bot = TeleBot(TOKEN)


user_orders = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Assalomu alaykum. Men KFC yetkazib berish xizmati botiman!\n"
        "Привет! Я бот службы доставки KFC!\n"
        "Hi! I am KFC delivery service bot!"
    )
    bot.send_message(message.chat.id, welcome_text)
    send_options(message)


def send_options(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    buttons = [
        types.KeyboardButton("📍 Joylashuv yuborish", request_location=True),
        types.KeyboardButton("📞 Kontaktni yuborish", request_contact=True),
        types.KeyboardButton("❌ Bekor qilish")
    ]

    markup.add(*buttons)

    bot.send_message(
        chat_id=message.chat.id,
        text="Quyidagilardan birini tanlang:",
        reply_markup=markup
    )


@bot.message_handler(content_types=['location', 'contact'])
def after_data_received(message):
    bot.send_message(message.chat.id, "Ma'lumotlar qabul qilindi.")
    send_city_menu(message.chat.id)


def send_city_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)

    cities = ["TOSHKENT", "SAMARQAND", "ANDIJAN", "KOKAND", "FARG'ONA", "URGANCH"]
    buttons = [types.InlineKeyboardButton(text=city, callback_data=city.lower()) for city in cities]

    markup.add(*buttons)

    bot.send_message(chat_id, "Quyidagilardan birini tanlang:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['toshkent', 'samarqand', 'andijan', 'kokand', "farg'ona", 'urganch'])
def handle_city_selection(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"{call.data.upper()} shahri tanlandi.")
    send_main_menu(call.message.chat.id)


def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    markup.add(
        types.KeyboardButton("🛒 Buyurtma berish"),
        types.KeyboardButton("🛍 Buyurtmalarim"),
        types.KeyboardButton("✍️ Fikr bildirish"),
        types.KeyboardButton("⚙️ Sozlamalar")
    )

    bot.send_message(chat_id, "Quyidagilardan birini tanlang:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "Buyurtma bekor qilindi.")

    elif message.text == "🛒 Buyurtma berish":
        send_media(message)

    elif message.text == "🛍 Buyurtmalarim":
        orders = user_orders.get(message.chat.id)
        if orders:
            order_list = "\n".join([f"- {item}" for item in orders])
            bot.send_message(message.chat.id, f"Sizning buyurtmalaringiz:\n{order_list}")
        else:
            bot.send_message(message.chat.id, "Siz hali hanuz birorta ham buyurtma bermagansiz.")

    elif message.text == "✍️ Fikr bildirish":
        msg = bot.send_message(message.chat.id, "Fikr va mulohazalaringizni yozing:")
        bot.register_next_step_handler(msg, handle_feedback)

    elif message.text == "⚙️ Sozlamalar":
        bot.send_message(message.chat.id, "Sozlamalar bo‘limi hali mavjud emas.")

    else:
        bot.send_message(message.chat.id, "Iltimos, menyudan tanlang.")


def send_media(message):
    try:
        with open("kfc.jpg", "rb") as image:
            markup = types.InlineKeyboardMarkup(row_width=2)
            menu_items = ["Zinger", "Twister", "Strips", "KFC Box", "Pepsi", "Kartoshka fri"]
            buttons = [types.InlineKeyboardButton(text=item, callback_data=f"order_{item}") for item in menu_items]
            markup.add(*buttons)

            bot.send_photo(
                message.chat.id,
                image,
                caption="KFC menyusidan birini tanlang:",
                reply_markup=markup
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"Rasm yuklashda xatolik: {e}")
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_food_selection(call):
    food = call.data.replace("order_", "")
    chat_id = call.message.chat.id

    if chat_id not in user_orders:
        user_orders[chat_id] = []
    user_orders[chat_id].append(food)

    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, f"✅ {food} buyurtmangiz qabul qilindi!")


def handle_feedback(message):
    bot.send_message(message.chat.id, "Rahmat! Fikringiz qabul qilindi.")


bot.polling(none_stop=True)