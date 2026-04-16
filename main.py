import time
import json
import os
import telebot

##TOKEN DETAILS
TOKEN = "Bee"

BOT_TOKEN = "7640369643:AAGPz013ccCbWxCDU_K2Y0SCLtiqo_rKvOw"
PAYMENT_CHANNEL = "@cipherinnovix"  # add payment channel here including the '@' sign
OWNER_ID = 2052558036  # write owner's user id here.. get it from @MissRose_Bot by /id
CHANNELS = ["@cipherinnovix"]  # add channels to be checked here
Daily_bonus = 0.1  # Put daily bonus amount here!
Mini_Withdraw = 1.00  # minimum withdraw amount
Per_Refer = 0.01  # per refer bonus

bot = telebot.TeleBot(BOT_TOKEN)

# users.json ဖိုင် မရှိရင် အလိုအလျောက် ဖန်တီးပေးခြင်း
USERS_FILE = 'users.json'

def init_data():
    """users.json ဖိုင်ကို initialize လုပ်ခြင်း"""
    if not os.path.exists(USERS_FILE):
        default_data = {
            'total': 0,
            'totalwith': 0,
            'referred': {},
            'referby': {},
            'checkin': {},
            'DailyQuiz': {},
            'balance': {},
            'wallet': {},
            'withd': {},
            'id': {},
            'refer': {}
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_data, f)

def load_data():
    """users.json ဖိုင်ကို ဖတ်ခြင်း"""
    try:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        # ensure all keys exist
        for key in ['total', 'totalwith', 'referred', 'referby', 'checkin',
                     'DailyQuiz', 'balance', 'wallet', 'withd', 'id', 'refer']:
            if key not in data:
                if key in ['total', 'totalwith']:
                    data[key] = 0
                else:
                    data[key] = {}
        return data
    except Exception:
        init_data()
        return load_data()

def save_data(data):
    """users.json ဖိုင်ကို သိမ်းခြင်း"""
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check(id):
    """User က channel join ထားလား စစ်ဆေးခြင်း"""
    try:
        for i in CHANNELS:
            member = bot.get_chat_member(i, id)
            if member.status in ['left', 'kicked']:
                return False
        return True
    except Exception:
        return False

bonus = {}

def menu(id):
    """Main menu ပြခြင်း"""
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊Statistics')
    bot.send_message(id, "*🏡 Home*", parse_mode="Markdown",
                     reply_markup=keyboard)

def get_join_msg():
    """Channel join message ဖန်တီးခြင်း"""
    msg = "*🍔 ဒီ Bot ကို အသုံးပြုဖို့ အောက်ပါ Channel ကို Join ရပါမယ် -"
    for i in CHANNELS:
        msg += f"\n➡️ {i}"
    msg += "*"
    return msg

def get_join_markup():
    """Join button markup ဖန်တီးခြင်း"""
    markup = telebot.types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(telebot.types.InlineKeyboardButton(
            text=f'📢 {ch}', url=f'https://t.me/{ch.replace("@", "")}'))
    markup.add(telebot.types.InlineKeyboardButton(
        text='✅ Joined', callback_data='check'))
    return markup

def ensure_user(data, user):
    """User data ရှိမရှိ စစ်ပြီး မရှိရင် ဖန်တီးခြင်း"""
    if user not in data['referred']:
        data['referred'][user] = 0
        data['total'] = data['total'] + 1
    if user not in data['checkin']:
        data['checkin'][user] = 0
    if user not in data['DailyQuiz']:
        data['DailyQuiz'][user] = "0"
    if user not in data['balance']:
        data['balance'][user] = 0
    if user not in data['wallet']:
        data['wallet'][user] = "none"
    if user not in data['withd']:
        data['withd'][user] = 0
    if user not in data['id']:
        data['id'][user] = data['total'] + 1
    return data

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.chat.id
        user = str(user_id)
        msg = message.text
        data = load_data()

        if msg == '/start':
            # Direct start (no referral)
            data = ensure_user(data, user)
            if user not in data['referby']:
                data['referby'][user] = user
            save_data(data)

            bot.send_message(user_id, get_join_msg(),
                             parse_mode="Markdown", reply_markup=get_join_markup())
        else:
            # Start with referral
            refid = msg.split()[1] if len(msg.split()) > 1 else user
            data = ensure_user(data, user)
            if user not in data['referby']:
                data['referby'][user] = refid
            save_data(data)

            bot.send_message(user_id, get_join_msg(),
                             parse_mode="Markdown", reply_markup=get_join_markup())
    except Exception as e:
        print(f"Start error: {e}")
        bot.send_message(message.chat.id, "⚠️ Error ဖြစ်နေပါတယ်။ ခဏစောင့်ပေးပါ။")
        bot.send_message(OWNER_ID, f"❌ Bot error on /start\nUser: {message.chat.id}\nError: {str(e)[:200]}")

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    try:
        user_id = call.message.chat.id
        user = str(user_id)

        if call.data == 'check':
            if check(user_id):
                data = load_data()
                bot.answer_callback_query(
                    callback_query_id=call.id, text='✅ Join ပြီးပါပြီ! အခု ငွေရှာလို့ရပါပြီ!')
                bot.delete_message(call.message.chat.id, call.message.message_id)

                if user not in data.get('refer', {}):
                    if 'refer' not in data:
                        data['refer'] = {}
                    data['refer'][user] = True

                    if user not in data['referby']:
                        data['referby'][user] = user

                    # Referral bonus ပေးခြင်း
                    if int(data['referby'][user]) != user_id:
                        ref_id = data['referby'][user]
                        ref = str(ref_id)
                        if ref not in data['balance']:
                            data['balance'][ref] = 0
                        if ref not in data['referred']:
                            data['referred'][ref] = 0
                        data['balance'][ref] += Per_Refer
                        data['referred'][ref] += 1
                        save_data(data)
                        bot.send_message(
                            ref_id, f"*🏧 Referral အသစ်! +{Per_Refer} {TOKEN} ရရှိပါပြီ!*", parse_mode="Markdown")
                        return menu(call.message.chat.id)
                    else:
                        save_data(data)
                        return menu(call.message.chat.id)
                else:
                    save_data(data)
                    menu(call.message.chat.id)
            else:
                bot.answer_callback_query(
                    callback_query_id=call.id, text='❌ Channel ကို Join မလုပ်ရသေးပါ!')
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, get_join_msg(),
                                 parse_mode="Markdown", reply_markup=get_join_markup())
    except Exception as e:
        print(f"Callback error: {e}")
        bot.send_message(call.message.chat.id, "⚠️ Error ဖြစ်နေပါတယ်။ ခဏစောင့်ပေးပါ။")
        bot.send_message(OWNER_ID, f"❌ Bot error on callback\nError: {str(e)[:200]}")

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        user_id = message.chat.id
        user = str(user_id)

        if message.text == '🆔 Account':
            data = load_data()
            if user not in data['balance']:
                data['balance'][user] = 0
            if user not in data['wallet']:
                data['wallet'][user] = "none"
            save_data(data)

            balance = data['balance'][user]
            wallet = data['wallet'][user]
            accmsg = f'*👮 User : {message.from_user.first_name}\n\n⚙️ Wallet :* `{wallet}`\n\n*💸 Balance :* `{balance}` *{TOKEN}*'
            bot.send_message(message.chat.id, accmsg, parse_mode="Markdown")

        elif message.text == '🙌🏻 Referrals':
            data = load_data()
            bot_name = bot.get_me().username
            if user not in data['referred']:
                data['referred'][user] = 0
            save_data(data)

            ref_count = data['referred'][user]
            ref_link = f'https://telegram.me/{bot_name}?start={message.chat.id}'
            ref_msg = f"*⏯️ Total Invites : {ref_count} Users\n\n👥 Referral System\n\n🥇 Level 1 - {Per_Refer} {TOKEN}\n\n🔗 Referral Link ⬇️\n{ref_link}*"
            bot.send_message(message.chat.id, ref_msg, parse_mode="Markdown")

        elif message.text == "⚙️ Set Wallet":
            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            keyboard.row('🚫 Cancel')
            bot.send_message(message.chat.id, "_⚠️ TRX Wallet Address ပို့ပေးပါ။_",
                             parse_mode="Markdown", reply_markup=keyboard)
            bot.register_next_step_handler(message, trx_address)

        elif message.text == "🎁 Bonus":
            cur_time = int(time.time())
            data = load_data()
            if user not in data['balance']:
                data['balance'][user] = 0

            if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 60 * 60 * 24):
                data['balance'][user] += Daily_bonus
                bonus[user_id] = cur_time
                save_data(data)
                bot.send_message(
                    user_id, f"🎉 *{Daily_bonus} {TOKEN} ရရှိပါပြီ!*", parse_mode="Markdown")
            else:
                remaining = (bonus[user_id] + 86400) - cur_time
                hours = remaining // 3600
                mins = (remaining % 3600) // 60
                bot.send_message(
                    message.chat.id, f"❌ *24 နာရီ တစ်ခါပဲ ရနိုင်ပါတယ်!\n⏰ နောက် {hours} နာရီ {mins} မိနစ် စောင့်ပါ။*", parse_mode="Markdown")

        elif message.text == "📊Statistics":
            data = load_data()
            msg = f"*📊 Total Members : {data['total']} Users\n\n🥊 Total Withdraw : {data['totalwith']} {TOKEN}*"
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == "💸 Withdraw":
            data = load_data()
            if user not in data['balance']:
                data['balance'][user] = 0
            if user not in data['wallet']:
                data['wallet'][user] = "none"
            save_data(data)

            bal = data['balance'][user]
            wall = data['wallet'][user]
            if wall == "none":
                bot.send_message(user_id, "_❌ Wallet မသတ်မှတ်ရသေးပါ။ ⚙️ Set Wallet ကို နှိပ်ပါ။_",
                                 parse_mode="Markdown")
                return
            if bal >= Mini_Withdraw:
                bot.send_message(user_id, "_💰 ထုတ်ယူမည့် ပမာဏကို ရိုက်ထည့်ပါ_",
                                 parse_mode="Markdown")
                bot.register_next_step_handler(message, amo_with)
            else:
                bot.send_message(
                    user_id, f"_❌ Balance မလုံလောက်ပါ။ အနည်းဆုံး {Mini_Withdraw} {TOKEN} ရှိမှ ထုတ်ယူနိုင်ပါတယ်။_", parse_mode="Markdown")

    except Exception as e:
        print(f"Text handler error: {e}")
        bot.send_message(message.chat.id, "⚠️ Error ဖြစ်နေပါတယ်။ ခဏစောင့်ပေးပါ။")
        bot.send_message(OWNER_ID, f"❌ Bot error on: {message.text}\nError: {str(e)[:200]}")

def trx_address(message):
    try:
        if message.text == "🚫 Cancel":
            return menu(message.chat.id)
        if len(message.text) == 34:
            user = str(message.chat.id)
            data = load_data()
            data['wallet'][user] = message.text
            save_data(data)
            bot.send_message(message.chat.id, "*💹 TRX Wallet သတ်မှတ်ပြီးပါပြီ: " +
                             data['wallet'][user] + "*", parse_mode="Markdown")
            return menu(message.chat.id)
        else:
            bot.send_message(
                message.chat.id, "*⚠️ TRX Address မမှန်ပါ! (34 လုံး ရှိရပါမယ်)*", parse_mode="Markdown")
            return menu(message.chat.id)
    except Exception as e:
        print(f"Wallet error: {e}")
        bot.send_message(message.chat.id, "⚠️ Error ဖြစ်နေပါတယ်။ ခဏစောင့်ပေးပါ။")

def amo_with(message):
    try:
        user_id = message.chat.id
        user = str(user_id)
        amo = message.text
        data = load_data()

        if user not in data['balance']:
            data['balance'][user] = 0
        if user not in data['wallet']:
            data['wallet'][user] = "none"

        bal = data['balance'][user]
        wall = data['wallet'][user]

        # ဂဏန်းစစ်ဆေးခြင်း
        try:
            amo_float = float(amo)
        except ValueError:
            bot.send_message(
                user_id, "_📛 ဂဏန်းသာ ရိုက်ထည့်ပါ။ ပြန်ကြိုးစားပါ။_", parse_mode="Markdown")
            return

        if amo_float < Mini_Withdraw:
            bot.send_message(
                user_id, f"_❌ အနည်းဆုံး {Mini_Withdraw} {TOKEN} ထုတ်ယူရပါမယ်_", parse_mode="Markdown")
            return
        if amo_float > bal:
            bot.send_message(
                user_id, "_❌ Balance ထက် ပိုထုတ်လို့ မရပါ_", parse_mode="Markdown")
            return

        amo_val = float(amo)
        data['balance'][user] -= amo_val
        data['totalwith'] += amo_val
        bot_name = bot.get_me().username
        save_data(data)

        bot.send_message(user_id, f"✅ *Withdraw request ပို့ပြီးပါပြီ!\n\n💹 Payment Channel :- {PAYMENT_CHANNEL}*", parse_mode="Markdown")

        markupp = telebot.types.InlineKeyboardMarkup()
        markupp.add(telebot.types.InlineKeyboardButton(text='🍀 BOT LINK', url=f'https://telegram.me/{bot_name}?start={OWNER_ID}'))

        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        withdraw_msg = (
            f"✅ *New Withdraw*\n\n"
            f"⭐ Amount - {amo_val} {TOKEN}\n"
            f"🦁 User - @{username}\n"
            f"💠 Wallet - `{data['wallet'][user]}`\n"
            f"☎️ User Referrals = {data['referred'].get(user, 0)}\n\n"
            f"🏖 Bot - @{bot_name}"
        )
        bot.send_message(PAYMENT_CHANNEL, withdraw_msg,
                         parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markupp)

    except Exception as e:
        print(f"Withdraw error: {e}")
        bot.send_message(message.chat.id, "⚠️ Error ဖြစ်နေပါတယ်။ ခဏစောင့်ပေးပါ။")
        bot.send_message(OWNER_ID, f"❌ Bot error on withdraw\nError: {str(e)[:200]}")


if __name__ == '__main__':
    init_data()
    print("🤖 Bot starting...")
    print(f"   Token: {TOKEN}")
    print(f"   Channels: {CHANNELS}")
    print(f"   Daily Bonus: {Daily_bonus}")
    print(f"   Per Refer: {Per_Refer}")
    print(f"   Min Withdraw: {Mini_Withdraw}")
    print("✅ Bot is running!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
