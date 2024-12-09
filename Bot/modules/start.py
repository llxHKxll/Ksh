from config import app
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import create_db, add_user, ensure_user_exists, get_user, update_points, update_level, update_health, connect_db

create_db()  # Ensure the table is created if it doesn't exist

@app.on_message(filters.command("start"))
def start_handler(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name  # Use first name for the link
    username = message.from_user.username or first_name

    # Ensure user exists in the database
    ensure_user_exists(user_id, username)

    # Fetch user data from the database
    user_data = get_user(user_id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed, xp_booster_expiry = user_data

        # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'

        # Inline keyboard with a button to your chat group
        chat_group_url = "https://t.me/KaisenWorld"  # Replace with your group link
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Join Chat Group", url=chat_group_url)]
            ]
        )

        # Send a welcome message with user data and the user link
        message.reply_photo(
            photo="https://imgur.com/a/EvmGYI7",
            caption=(
                f"Hey {user_link}, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝖯𝗒𝗑𝗇 𝖡𝗈𝗍 ! 🎉\n\n"
                f"<b>📜 ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴛᴏᴋᴇɴs ?</b>\n"
                f"- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴄᴏɪɴs.\n\n"
                f"𝖦𝖾𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗇𝗈𝗐 ! 𝗍𝗒𝗉𝖾 /help 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.\n\n"
                f"🎯 **ʏᴏᴜʀ sᴛᴀᴛs :**\n• ᴄᴏɪɴs : {points} | • ʟᴇᴠᴇʟ : {level}"
            ),
            reply_markup=keyboard,  # Attach the keyboard to the message
        )

    # If user data doesn't exist, add the user and fetch data again
    if user_data is None:
        add_user(user_id, username)
        user_data = get_user(user_id)
