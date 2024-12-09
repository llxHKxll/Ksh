import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Bot.KEYS import BOT_ADMIN_ID
from config import app

polls = {}  # Store polls in memory

@app.on_message(filters.command("poll"))
def poll_handler(client, message):
    """Handle the /poll command to create polls."""
    user_id = message.from_user.id

    # Ensure only admin can create polls
    if user_id != BOT_ADMIN_ID:
        message.reply("You need to be a bot admin to create a poll.")
        return

    # Parse the command
    command_text = message.text[len("/poll "):].strip()  # Remove command prefix
    if not command_text.startswith("\"") or "\"" not in command_text[1:]:
        message.reply("Usage: /poll \"<question>\" \"<option1>\" \"<option2>\" ...")
        return

    # Extract question
    question_end_index = command_text.index("\"", 1)  # Find closing quote for the question
    question = command_text[1:question_end_index].strip()

    # Extract remaining text (options)
    remaining_text = command_text[question_end_index + 1:].strip()

    # Use regex to extract options in quotes
    options = re.findall(r'"([^"]+)"', remaining_text)

    # Validate options
    if len(options) < 2:
        message.reply("Please provide at least two options for the poll.")
        return

    # Start the poll (no expiry time argument)
    start_poll(client, message, question, options)

@app.on_callback_query(filters.regex(r"vote_\d+_.*"))
def vote_handler(client, callback_query):
    """Handle user votes."""
    handle_vote(client, callback_query)

@app.on_message(filters.command("results"))
def results_handler(client, message):
    """Show poll results."""
    try:
        poll_id = int(message.text.split()[1])  # Extract poll_id from the message
        show_poll_results(client, message, poll_id)
    except (ValueError, IndexError):
        message.reply("Usage: /results <poll_id>")

def is_bot_admin(user_id):
    """Check if the user is a bot admin."""
    return user_id == BOT_ADMIN_ID


def start_poll(client, message, question, options):
    """Start a poll created by bot admin."""
    if not is_bot_admin(message.from_user.id):
        message.reply("You need to be a bot admin to create a poll.")
        return

    poll_id = len(polls) + 1  # Create a unique poll ID
    polls[poll_id] = {
        "question": question,
        "options": options,
        "votes": {option: 0 for option in options},
        "voters": set(),
    }

    # Inline buttons for voting
    buttons = [
        [InlineKeyboardButton(option, callback_data=f"vote_{poll_id}_{option}")]
        for option in options
    ]

    # Send poll message
    message.reply_text(
        text=f"**Poll ID #{poll_id}**\n{question}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


def handle_vote(client, callback_query):
    """Handle voting on a poll."""
    data = callback_query.data.split("_")
    poll_id = int(data[1])
    vote_option = "_".join(data[2:])

    if poll_id not in polls:
        callback_query.answer("Poll does not exist or has ended.")
        return

    poll = polls[poll_id]

    # Prevent multiple votes
    if callback_query.from_user.id in poll["voters"]:
        callback_query.answer("You've already voted in this poll.")
        return

    # Record vote
    if vote_option in poll["votes"]:
        poll["votes"][vote_option] += 1
        poll["voters"].add(callback_query.from_user.id)
        callback_query.answer(f"Thanks for voting! You voted for: {vote_option}")
    else:
        callback_query.answer("Invalid option.")


def show_poll_results(client, message, poll_id):
    """Show the results of the poll."""
    if poll_id not in polls:
        message.reply("Invalid poll ID or the poll has ended.")
        return

    poll = polls[poll_id]
    results_text = f"**Poll Results for ID #{poll_id}**\n{poll['question']}\n\n"

    for option, vote_count in poll["votes"].items():
        results_text += f"{option}: {vote_count} votes\n"

    message.reply_text(results_text)
