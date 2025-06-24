import telebot
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

from ui import setup_ui_handlers
import b3   # Use b3.py handlers for new commands
import gen
import bin as bin_lookup
import fake
import scr
import status

# --- UI/menus ---
AUTHORIZED_USERS = {}
def save_auth(data): pass
def is_authorized(user_id): return True

setup_ui_handlers(bot, AUTHORIZED_USERS, save_auth, is_authorized)

# --- Main command handlers ---

# Remove old /chk and /mchk handlers
# @bot.message_handler(commands=['chk'])
# def handle_chk_command(message):
#     chk.handle_chk(bot, message)

# @bot.message_handler(commands=['mchk'])
# def handle_mchk_command(message):
#     chk.handle_mchk(bot, message)

# Add new /b3 and /mb3 handlers with new UI
@bot.message_handler(commands=['b3'])
def handle_b3_command(message):
    b3.handle_b3(bot, message)

@bot.message_handler(commands=['mb3'])
def handle_mb3_command(message):
    b3.handle_mb3(bot, message)

# Keep /chktxt if you want file card checking (using chk.py or adapt to b3)
@bot.message_handler(commands=['chktxt'], content_types=['document'])
def handle_chktxt_command(message):
    # Use chk or b3 handler depending on your implementation
    # For now, keeping chk's handler for file input
    import chk
    chk.handle_chktxt(bot, message)

@bot.message_handler(commands=['gen'])
def handle_gen_command(message):
    gen.handle_gen(bot, message)

@bot.message_handler(commands=['bin'])
def handle_bin_command(message):
    bin_lookup.handle_bin(bot, message)

@bot.message_handler(commands=['fake'])
def handle_fake_command(message):
    fake.handle_fake(bot, message)

@bot.message_handler(commands=['scr'])
def handle_scr_command(message):
    scr.handle_scr(bot, message)

@bot.message_handler(commands=['status'])
def handle_status_command(message):
    status.handle_status(bot, message)

if __name__ == "__main__":
    print("🐰 Bunny Bot is running...")
    bot.infinity_polling()
