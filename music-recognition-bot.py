import telebot
import logging 
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup



logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

API_TOKEN = '< ADD TOKEN >'
bot = telebot.TeleBot(API_TOKEN)
CHANNEL_USERNAME = "< CHANNEL USERNAME >" 

state = {"valid": 0}

@bot.message_handler(commands=['start'])
def start(message):
    user_id_check = str(message.from_user.id)
    user_id = message.from_user.id
    state["valid"] = 0
    with open("users.txt", "r+") as file:
        data = file.read()
        if user_id_check not in data:
            file.write(user_id_check + "\n")
        else :
            pass
        file.close()
    bot.reply_to(message, "سلام، به ربات تشخیص آهنگ خوش آمدید ! ✨🥳")
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("📢 عضویت در کانال گوربه میوزیک", url="https://t.me/justmeowsic")
    markup.add(button)
    bot.send_message(
        message.chat.id,
        "برای استفاده از امکانات ربات، ابتدا باید در کانال  میوزیک عضو شوید:",
        reply_markup=markup
    )
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            markup = ReplyKeyboardMarkup(one_time_keyboard=True,row_width=2,resize_keyboard=True)
            markup.add(KeyboardButton("تشخیص آهنگ"))
            bot.send_message(message.chat.id, "🎉 خوش آمدید! شما عضو کانال هستید و می‌توانید از ربات استفاده کنید.",reply_markup=markup)
        else:
            bot.reply_to(message, f"⛔️ ابتدا باید عضو کانال ما بشید ! \n بعد عضویت، مجدد روی استارت بزنید.")
    except Exception as e:
        bot.reply_to(message, f"⛔️ شما عضو کانال نیستید.")

def send_welcome(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True,row_width=2,resize_keyboard=True)
    markup.add(KeyboardButton("تشخیص آهنگ"))
    bot.send_message(message.chat.id, "هر وقت نیاز داشتی روی تشخیص آهنگ بزن ✨",reply_markup=markup)

def check_membership(message):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)

        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            markup = InlineKeyboardMarkup()
            button = InlineKeyboardButton("📢 عضویت در کانال گوربه میوزیک", url="https://t.me/justmeowsic")
            markup.add(button)
            bot.send_message(message.chat.id, "⛔️ برای استفاده از امکانات ربات، ابتدا عضو کانال ما شوید!",reply_markup=markup)
            return False
    except Exception as e:
        bot.reply_to(message, "⛔️ مشکلی در بررسی عضویت شما پیش آمد. لطفاً دوباره امتحان کنید.")
        return False

@bot.message_handler(func=lambda message: message.text == "تشخیص آهنگ")
def first_check(message):
    if check_membership(message):
        state["valid"] = 1
        audio_recognition(message)
    else:
        state["valid"] =0
        send_welcome(message)

def audio_recognition(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton("منصرف شدم!"))
    bot.reply_to(
        message,
        "خیلی خب، حالا ویس یا فایل صوتی و یا حتی ویدیو رو بفرست تا آهنگشو تشخیص بدم\n🔰 مدت صدا بهتره حداقل ۶ ثانیه باشه!",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "منصرف شدم!")
def cancel_process(message):
    state["valid"] = 0
    bot.send_message(message.chat.id, "حله !")
    send_welcome(message)

@bot.message_handler(content_types=['video'],func= lambda message: message.text!="منصرف شدم!")
def audio_recognition_3(message):
    if state['valid'] ==1 :
        try:

            file_info = bot.get_file(message.video.file_id)
            file_name = f"voice_{message.message_id}.ogg"
            downloaded_file = bot.download_file(file_info.file_path)
            bot.send_message(message.chat.id,"در حال جست وجو 🐈 ...")

            data = {
                'api_token': 'f703912781e33b8beaad0a4e840f5d4f',
                'return': 'spotify',
            }
            
            files = {
                'file': ('audio.ogg', downloaded_file)
            }
            
            response = requests.post('https://api.audd.io/', data=data, files=files)
            result = response.json()
            if result.get('result'):
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
                message_text = f"""
                \n  
                <b> اطلاعات آهنگ: </b>
                \n
                🎧 نام: {result['result']['title']}\n
                👤 خواننده: {result['result']['artist']}\n
                📅 تاریخ انتشار: {result['result']['release_date']}\n
                🔗 لینک پخش : {result['result']['song_link']}\n
    """ 
                bot.reply_to(message, "هورااااا ! آهنگ پیدا شد 🥳")
                bot.send_message(message.chat.id,message_text,parse_mode="HTML")
            
            else:
                bot.reply_to(message, "متاسفانه نتونستم این آهنگ رو شناسایی کنم!")
                
        except Exception as e:
            bot.reply_to(message, "مشکلی پیش اومد! لطفا دوباره تلاش کنید.")

        state["valid"] = 0
        send_welcome(message)
    else:
        state["valid"] = 0



@bot.message_handler(content_types=['voice','audio'],func= lambda message: message.text!="منصرف شدم!")
def audio_recognition_2(message):
    if state['valid'] == 1 :
        try:

            file_info = bot.get_file(message.voice.file_id)
            file_name = f"voice_{message.message_id}.ogg"
            downloaded_file = bot.download_file(file_info.file_path)
            bot.send_message(message.chat.id,"در حال جست وجو 🐈 ...")

            data = {
                'api_token': 'f703912781e33b8beaad0a4e840f5d4f',
                'return': 'spotify',
            }
            
            files = {
                'file': ('audio.ogg', downloaded_file)
            }
            
            response = requests.post('https://api.audd.io/', data=data, files=files)
            result = response.json()
            if result.get('result'):
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
                message_text = f"""
                \n  
                <b> اطلاعات آهنگ: </b>
                \n
                🎧 نام: {result['result']['title']}\n
                👤 خواننده: {result['result']['artist']}\n
                📅 تاریخ انتشار: {result['result']['release_date']}\n
                🔗 لینک پخش : {result['result']['song_link']}\n
    """ 
                bot.reply_to(message, "هورااااا ! آهنگ پیدا شد 🥳")
                bot.send_message(message.chat.id,message_text,parse_mode="HTML")
            
            else:
                bot.reply_to(message, "متاسفانه نتونستم این آهنگ رو شناسایی کنم!")
                
        except Exception as e:
            bot.reply_to(message, "مشکلی پیش اومد! لطفا دوباره تلاش کنید.")
        state["valid"] = 0
        send_welcome(message)
    else:
        state["valid"] = 0

@bot.message_handler(func=lambda message: message.text == "%آمار")
def stats(message):
    logging.info('hi')
    if  message.chat.id==" id " :
        with open("users.txt", "r+") as file:
            lines = file.readlines()
            line_count = len(lines)
            bot.send_message(message.chat.id,f"تعداد کاربران :\n {line_count}")
        file.close()

bot.infinity_polling()
