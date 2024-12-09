from pyrogram import Client, filters
import random  # For generating random success/fail chance and damage/rewards
from pyrogram.types import Message  # For working with messages
from config import app
from database.db_manager import get_user, update_health, update_points  # Replace 'your_database_module' with the actual module name

@app.on_message(filters.command("kill"))
async def kill_handler(client, message: Message):
    """Handle the /kill command to reduce another user's health with chances and reward."""
    user_id = message.from_user.id

    # Ensure /kill is used by replying to another user's message
    if not message.reply_to_message:
        await message.reply("You must reply to another user's message to use /kill!")
        return

    target_user = message.reply_to_message.from_user

    # Prevent killing bots
    if target_user.is_bot:
        await message.reply("You can't kill a bot.")
        return

    # Fetch attacker (user) and target's data from the database
    user_data = get_user(user_id)
    target_user_data = get_user(target_user.id)
    if not user_data or not target_user_data:
        await message.reply("User or target not found.")
        return

    user_health = user_data[5]  # User's health
    target_health = target_user_data[5]  # Target's current health

    # If the user has 0 health, they cannot kill anyone
    if user_health <= 0:
        await message.reply("You have to restore your health first!")
        return

    # If the target user is already dead, prevent killing
    if target_health <= 0:
        await message.reply(f"{target_user.first_name} has already died and cannot be killed!")
        return

    # Add a 50% chance of failing the kill attempt (You can modify the chance)
    kill_success = random.choice([True, False])  # 50% chance (True or False)

    if not kill_success:
        await message.reply(f"Failed to kill {target_user.first_name}. Better luck next time!")
        return

    # Random damage between 5 and 20
    damage = random.randint(5, 20)
    
    # Apply the damage, ensuring health doesn't go below 0
    new_health = max(target_health - damage, 0)
    
    # Update the target user's health in the database
    update_health(target_user.id, new_health)

    # Reward points for successful kill
    reward_points = random.randint(3, 24)
    update_points(user_id, reward_points)  # Add the reward points to the attacker

    # Send a message indicating the result of the kill
    if new_health > 0:
        await message.reply(f"{target_user.first_name} has been attacked and lost {damage} health! Current health: {new_health}%. You earned {reward_points} points!")
    else:
        await message.reply(f"{target_user.first_name} has been killed! Their health is now 0%. You earned {reward_points} points!")
