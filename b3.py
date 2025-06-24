# chk.py
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from p import check_card, parse_check_card_result

# B3 UI Formatter
def format_card_check_result(
    card, gateway, status_key, response, bank, country_flag,
    card_type, bin_code, check_time, checked_by, dev_link="https://t.me/bunny2050"
):
    status_map = {
        "approved": ("𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗", "✅"),
        "declined": ("𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗", "❌"),
        "insufficient_funds": ("𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗙𝗨𝗡𝗗𝗦", "⚠️"),
        "3d_issue": ("𝟯𝗗 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 𝗜𝗦𝗦𝗨𝗘", "🔒"),
    }
    status_text, status_emoji = status_map.get(status_key.lower(), ("𝗨𝗡𝗞𝗡𝗢𝗪𝗡", "❓"))
    message = (
        f"🔍 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 𝗖𝗮𝗿𝗱: {card}\n"
        f"🚪 𝗚𝗮𝘁𝗲𝘄𝗮𝘆: {gateway}\n"
        f"🕵️ 𝗦𝘁𝗮𝘁𝘂𝘀: {status_text} {status_emoji}\n"
        f"💬 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {response}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 𝗕𝗮𝗻𝗸: {bank}\n"
        f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country_flag}\n"
        f"💡 𝗜𝗻𝗳𝗼: {card_type}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 𝗕𝗜𝗡: {bin_code}\n"
        f"⏱️ 𝗧𝗶𝗺𝗲: {check_time}\n"
        f"👤 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {checked_by} 🐰\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 𝗗𝗲𝘃: <a href='{dev_link}'>𝗕𝗨𝗡𝗡𝗬 🚀</a>"
    )
    return message

# /b3 Handler (Single Card)
def handle_b3(bot, message):
    args = message.text.split(None, 1)
    if len(args) < 2 or "|" not in args[1]:
        bot.reply_to(message, "❌ Send as: <code>/b3 4556737586899855|12|2026|123</code>", parse_mode="HTML")
        return
    card_line = args[1].strip()
    if card_line.count('|') != 3 or "\n" in card_line:
        bot.reply_to(message, "❌ Only ONE card per /b3.")
        return

    reply_msg = bot.reply_to(message, "🔄 <b>Processing B3 check...</b>", parse_mode="HTML")

    def check_and_reply():
        try:
            result = check_card(card_line)
            info = parse_check_card_result(result, default_card=card_line)
            checked_by = message.from_user.first_name or (message.from_user.username if message.from_user else "User")
            formatted_msg = format_card_check_result(
                info['card'], info['gateway'], info['status_key'], info['response'],
                info['bank'], info['country_flag'], info['card_type'],
                info['bin_code'], info['check_time'], checked_by
            )
            bot.edit_message_text(formatted_msg, message.chat.id, reply_msg.message_id,
                                  parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {e}", message.chat.id, reply_msg.message_id)
    threading.Thread(target=check_and_reply).start()

# /mb3 Handler (Mass Cards)
def handle_mb3(bot, message):
    cards_text = ""
    if message.reply_to_message and message.reply_to_message.text:
        cards_text = message.reply_to_message.text
    else:
        args = message.text.split(None, 1)
        if len(args) > 1:
            cards_text = args[1]

    card_lines = [line.strip() for line in cards_text.splitlines() if "|" in line]
    if not card_lines:
        bot.reply_to(message, "❌ No cards found!")
        return
    if len(card_lines) > 20:
        bot.reply_to(message, "❌ Max 20 cards at once with /mb3!")
        return

    approved = 0
    declined = 0
    checked = 0
    total = len(card_lines)

    status_markup = InlineKeyboardMarkup(row_width=1)
    status_markup.add(
        InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
        InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
        InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
        InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
    )
    status_msg = bot.reply_to(message, "━━━━━━━━━━━━━━━━━━━━━━", reply_markup=status_markup)

    def mass_check():
        nonlocal approved, declined, checked
        for card in card_lines:
            try:
                result = check_card(card)
                info = parse_check_card_result(result, default_card=card)
                checked_by = message.from_user.first_name or (message.from_user.username if message.from_user else "User")
                formatted_msg = format_card_check_result(
                    info['card'], info['gateway'], info['status_key'], info['response'],
                    info['bank'], info['country_flag'], info['card_type'],
                    info['bin_code'], info['check_time'], checked_by
                )
                bot.reply_to(message, formatted_msg, parse_mode="HTML", disable_web_page_preview=True)
                if info['status_key'] == "approved":
                    approved += 1
                else:
                    declined += 1
                checked += 1

                status_markup = InlineKeyboardMarkup(row_width=1)
                status_markup.add(
                    InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
                    InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
                )
                try:
                    bot.edit_message_reply_markup(status_msg.chat.id, status_msg.message_id, reply_markup=status_markup)
                except Exception:
                    pass
            except Exception:
                declined += 1
                checked += 1
        status_markup = InlineKeyboardMarkup(row_width=1)
        status_markup.add(
            InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
            InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
            InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
            InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
        )
        try:
            bot.edit_message_reply_markup(status_msg.chat.id, status_msg.message_id, reply_markup=status_markup)
        except Exception:
            pass

    threading.Thread(target=mass_check).start()

# Bot command registration (Add this where your TeleBot is created and configured)
# Example:
# import telebot
# bot = telebot.TeleBot('YOUR_TOKEN')
# 
# # Add handlers:
# bot.message_handler(commands=['b3'])(lambda message: handle_b3(bot, message))
# bot.message_handler(commands=['mb3'])(lambda message: handle_mb3(bot, message))
