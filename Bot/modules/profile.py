import random  # For generating random values for points, rewards, etc.
from time import time  # For tracking user activity time
from pyrogram import Client, filters  # For Pyrogram client and filters
from pyrogram.types import Message  # For working with Telegram messages
from config import app

# Assuming database utility functions are implemented in a separate module
from your_database_module import (
    get_user,  # To fetch user data from the database
    check_flood,  # To handle flood control
    level_up  # To handle leveling up based on activity
)

@app.on_message(filters.command("profile"))
async def profile_handler(client, message):
    """Handle the /profile command."""
    # Check if the command is replied to a message or tagged with @username
    if message.reply_to_message:
        # If the command is used by replying to another user's message
        target_user = message.reply_to_message.from_user
    elif message.entities and message.entities[0].type == "mention":
        # If the command is used by tagging a user (e.g., @username)
        target_user = message.entities[0].user
    else:
        # If no reply or mention, show the profile of the user who sent the command
        target_user = message.from_user

    # Check if the target is a bot
    if target_user.is_bot:
        await message.reply("You can't get the profile of a bot.")
        return

    # Fetch user data from the database for the target user
    user_data = get_user(target_user.id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed, xp_booster_expiry = user_data

        # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={target_user.id}">{target_user.first_name}</a>'

        # Format the last activity time
        time_diff = int(time()) - last_activity_time
        last_activity = format_time_diff(time_diff)

        # Prepare the profile text
        profile_text = f"""
        **{user_link}'s Profile:**
💎 **Level** : {level}
🎮 **Exp** : {exp}/{level * 100}
💰 **Points** : {points}
❤️ **Health** : {health}%
        
🕛 **Last Checkin** : {last_activity}

- **You're doing great! Keep chatting to level up!**
        """

        # Send the profile details
        await message.reply_text(profile_text)
    else:
        # If user data doesn't exist
        await message.reply_text(f"Error fetching {target_user.first_name}'s profile. Please try again later or use /start!")


def format_time_diff(seconds):
    """Convert seconds into a readable time format."""
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    else:
        return f"{seconds // 86400} days ago"

@app.on_message(filters.text)
async def handle_message(client, message):
    """Handle the flood control and leveling up based on chat activity."""
    # List of allowed group chat IDs (replace with your actual group IDs)
    ALLOWED_GROUPS = [-1002135192853, -1002324159284]  # Add your group IDs here

    # Ensure the message is from an allowed group
    if message.chat.id not in ALLOWED_GROUPS:
        return  # Ignore messages outside allowed groups

    user_id = message.from_user.id
  
    # Flood control logic
    if check_flood(user_id):
        await message.reply("You are sending messages too quickly. Please wait a few seconds!")
    else:
        # Increment experience and level based on the message content
        level_up(user_id, message.text)
