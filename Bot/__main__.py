import sys
import os
from flask import Flask
from threading import Thread
from config import app  # Import your Pyrogram bot

# Flask app to satisfy Render's port binding requirement
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    """Run the Flask server on the assigned Render port."""
    port = int(os.environ.get("PORT", 5000))  # Render provides the PORT environment variable
    flask_app.run(host="0.0.0.0", port=port)

def run_bot():
    """Run the Telegram bot."""
    app.run()

if __name__ == "__main__":
    # Run Flask and the bot in separate threads
    Thread(target=run_flask).start()
    run_bot()

import sys
import glob
import asyncio
import logging
import importlib
import urllib3


from pathlib import Path
from config import app


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_plugins(plugin_name):
    path = Path(f"Bot/modules/{plugin_name}.py")
    spec = importlib.util.spec_from_file_location(f"Bot.modules.{plugin_name}", path)
    load = importlib.util.module_from_spec(spec)
    load.logger = logging.getLogger(plugin_name)
    spec.loader.exec_module(load)
    sys.modules["Bot.modules." + plugin_name] = load
    print("Bot has been imported" + plugin_name)


files = glob.glob("Bot/modules/*.py")
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name.replace(".py", ""))

print("Bot Deployed Successfully !")


async def main():
    await Sv.run_until_disconnected()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
