import sys
import glob
import asyncio
import logging
import importlib.util
import urllib3
import os
from pathlib import Path
from threading import Thread
from flask import Flask
from config import app  # Assuming `app` is a Pyrogram Client instance

# Set up logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

# Disable SSL warnings (if necessary)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to dynamically load plugins
def load_plugins(plugin_name):
    path = Path(f"Bot/modules/{plugin_name}.py")
    if path.exists():
        # Create a module spec and load the module dynamically
        spec = importlib.util.spec_from_file_location(f"Bot.modules.{plugin_name}", path)
        module = importlib.util.module_from_spec(spec)
        module.logger = logging.getLogger(plugin_name)  # Assign a logger to the module
        spec.loader.exec_module(module)
        sys.modules[f"Bot.modules.{plugin_name}"] = module
        print(f"Plugin '{plugin_name}' has been imported successfully.")
    else:
        print(f"Plugin '{plugin_name}' not found at {path}.")

# Load all Python files in the 'Bot/modules' directory
files = glob.glob("Bot/modules/*.py")
for file in files:
    plugin_name = Path(file).stem  # Extract the plugin name without the '.py' extension
    load_plugins(plugin_name)

print("Bot Deployed Successfully!")

# Flask app to satisfy Render's port binding requirement
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    """Run the Flask server on the assigned Render port."""
    port = int(os.environ.get("PORT", 5000))  # Render provides the PORT environment variable
    flask_app.run(host="0.0.0.0", port=port)

# Run the bot (for Pyrogram)
async def run_bot():
    """Run the Telegram bot."""
    await app.run()  # Using `run()` for Pyrogram Client

# Entry point
if __name__ == "__main__":
    # Start Flask server in a separate thread
    Thread(target=run_flask).start()

    # Run the bot asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
