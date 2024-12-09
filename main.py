import sys
import glob
import asyncio
import logging
import importlib.util
import urllib3
from pathlib import Path
from config import app


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

# Asynchronous function to run the bot
async def main():
    await app.run_until_disconnected()

# Run the asynchronous event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
