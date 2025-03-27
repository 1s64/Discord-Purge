import requests
import time
import json

# load default values from cfg
CONFIG_FILE = "config.json"

print("--- Discord Message Purge | @1s64 ---\n")

try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    config_loaded = True

except Exception as e:
    print(f"⚠️ Unable to load {CONFIG_FILE}: {e}")
    config_loaded = False
    config = {}

# default values from cfg
DEFAULT_TOKEN = config.get("default_token", "")
DEFAULT_CHANNEL_ID = config.get("default_channel_id", "")
DEFAULT_USER_ID = config.get("default_user_id", "")

DEFAULT_DELAY = config.get("default_delay")
DEFAULT_DELAY2 = config.get("default_delay2")
DEFAULT_LIMIT_RATE = config.get("default_limit_rate")

# print function for config
def print_config():
    print(f"  > Token: {TOKEN}")
    print(f"  > Channel ID: {CHANNEL_ID}")
    print(f"  > User ID: {USER_ID}\n")
    print(f"  > Delay Value 1: {DELAY_VALUE}")
    print(f"  > Delay Value 2: {DELAY_VALUE2}")
    print(f"  > Limit Rate Delay: {LIMIT_RATE_VALUE}")

# use config input
if config_loaded == True:
    print(f"'{CONFIG_FILE}' Found!\n")
    initial_input = input("Use available config? (Y/N): ").strip().lower()
else:
    initial_input = "n"

# initial input if statement
if initial_input == 'y':
    print("\nUsing Config!\n")

    TOKEN, CHANNEL_ID, USER_ID = DEFAULT_TOKEN, DEFAULT_CHANNEL_ID, DEFAULT_USER_ID

    DELAY_VALUE, DELAY_VALUE2, LIMIT_RATE_VALUE = DEFAULT_DELAY, DEFAULT_DELAY2, DEFAULT_LIMIT_RATE
    
    print_config()
else:
    print("\nNot using config... (Manual User Data)\n")

    # user info
    print("Please enter User & Delay Info\n")

    inputs = {
        "TOKEN": "  > Enter your Discord token: ",
        "CHANNEL_ID": "  > Enter your Channel ID: ",
        "USER_ID": "  > Enter your User ID: ",
    }

    delay_inputs = {
        "DELAY_VALUE": "  > Enter delay rate (0.5, 1, etc.): ",
        "DELAY_VALUE2": "  > Enter second delay rate (1, 2, etc.): ",
        "LIMIT_RATE_VALUE": "  > Enter limit rate delay (2.5, 5, etc.): "
    }

    # input
    TOKEN = input(inputs["TOKEN"]).strip() or DEFAULT_TOKEN
    CHANNEL_ID = input(inputs["CHANNEL_ID"]).strip() or DEFAULT_CHANNEL_ID
    USER_ID = input(inputs["USER_ID"]).strip() or DEFAULT_USER_ID
    print("")
    DELAY_VALUE = input(delay_inputs["DELAY_VALUE"]).strip() or str(DEFAULT_DELAY)
    DELAY_VALUE2 = input(delay_inputs["DELAY_VALUE2"]).strip() or DEFAULT_DELAY2
    LIMIT_RATE_VALUE = input(delay_inputs["LIMIT_RATE_VALUE"]).strip() or DEFAULT_LIMIT_RATE

    print("\nUsing information...\n")
    print_config()

# headers
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
}

# keeping track
already_tried = set()
deleted_count = 0

# delete message func
def delete_message(message_id):
    global deleted_count

    if message_id in already_tried:
        return False
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/{message_id}"
    
    try:
        response = requests.delete(url, headers=HEADERS)
        
        # success
        if response.status_code == 204:
            deleted_count += 1
            print(f"✅ Deleted message: {message_id} ({deleted_count})")
            return True

        
        # rate limit
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)

            print(f"⚠️ Rate limited! Waiting {retry_after} seconds...")

            time.sleep(retry_after + LIMIT_RATE_VALUE)
            return delete_message(message_id)
        
        # error
        else:
            error_data = response.json()
            error_code = error_data.get("code", 0)
            
            if error_code == 50021:
                print(f"⚠️ Skipping system message {message_id}, cannot be deleted.")
                already_tried.add(message_id)
                return False
            else:
                print(f"❌ Failed to delete {message_id}: {response.text}")
                already_tried.add(message_id)
                return False
    
    except Exception as e:
        print(f"🚨 Error deleting {message_id}: {str(e)}")
        already_tried.add(message_id)
        return False

# acquire messages
def get_messages(before=None, limit=50):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages?limit={limit}"
    
    if before:
        url += f"&before={before}"
        
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch messages (Potentially wrong user-id, channel-id or token.): {response.text}")
        return []

# bulk deletion
def delete_my_messages():
    deleted_count = 0
    last_message_id = None

    while True:
        messages = get_messages(before=last_message_id)
        
        # if not messages break
        if not messages:
            break
            
        # update the last message ID for pagination
        last_message_id = messages[-1]["id"]
        
        user_messages = [msg for msg in messages if str(msg["author"]["id"]) == USER_ID]
        
        # if no user messages continue
        if not user_messages:
            continue
            
        # delete user messages
        for msg in user_messages:
            success = delete_message(msg["id"])
            if success:
                deleted_count += 1
            time.sleep(DELAY_VALUE)
    
    return deleted_count

# calling functions
try:
    print("\nStarting message deletion...\n")

    while True:
        deleted = delete_my_messages()

        if deleted == 0:
            print("\n✅ Complete! No more messages to delete.\n")
            break
        else:
            print(f"Deleted {deleted} messages. Checking for more...")
            time.sleep(DELAY_VALUE2)
    
except KeyboardInterrupt:
    print("\nScript stopped by user.")

except Exception as e:
    print(f"Script error: {str(e)}")
