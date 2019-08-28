import discord                  # Discord.py API
import requests                 # To download the files
import os                       # To create the necessary directories
import hashlib                  # To hash the given file

from datetime import datetime   # To print system date and time
from credentials import TOKEN   # Bot's token contained in credentials.py (ignored by git)

# Version Number
VERSION = "v0.9 - BETA BUILD"

# A list of commands with brief descriptions
help_block = "```" \
             "---HashBot HELP---" \
            "\n$hash - Hashes the attached file and sends a message containing the hash. Ex: $hash SHA256" \
            "\n$help - Sends this help message to the channel it was invoked in." \
            "\n$about - Sends a message containing information about this bot to the channel it was invoked in." \
            "```"

supported_hashes = ['SHA1', 'SHA256']

# A list of supported hashes as a string (to print)
supported_hashes_s = "```" \
                   "---List of Supported Hashes---\n" \
                   "SHA1, SHA256" \
                   "```"

about_string = "Version: " + VERSION + "\nBuilt by Daniel Kuzmin \nhttps://github.com/danielkuzmin"


# Creates the necessary directories if they do not exist
def create_directories():
    try:
        # This is where the requested file is stored while it's being hashed
        os.makedirs(r"HASHBOT_FILES\TEMPFILES")
        # This is where the logs are
        os.makedirs(r"HASHBOT_FILES\LOGS")
    except FileExistsError:
        pass


# Writes a log entry
def write_log(a_info, fhash, user):
    f = open("HASHBOT_FILES\LOGS\logs.txt", "a+")
    log = f"\n{a_info.id}\n---{datetime.now()}\n---{a_info.filename}\n---{a_info.url}\n---{fhash}\n---UserID : {user}"
    f.write(log)


def delete_file(filename):
    os.remove(f"HASHBOT_FILES\TEMPFILES\{filename}")


# Returns the hash of a file given the filename and hash function name
def hash_file(filename, hashname):
    file = open(f"HASHBOT_FILES\TEMPFILES\{filename}", 'rb')
    if hashname == 'SHA1':
        sha1 = hashlib.sha1(file.read()).hexdigest()
        return sha1
    if hashname == 'SHA256':
        sha256 = hashlib.sha256(file.read()).hexdigest()
        return sha256


# Saves the attached file to the temp folder
def save_to_temp(url, a_id, filename):
    r = requests.get(url)
    with open(f"HASHBOT_FILES\TEMPFILES\{a_id}-{filename}", 'wb') as f:
        f.write(r.content)


# Checks if the user entered a valid hash
def validate_input(hashname):
    return hashname in supported_hashes


# Message printed to the console when the bot starts
print(f'HashBot is powering up...')
print("Current System date and time: ", datetime.now())

client = discord.Client()

# Message printed to the console when the bot joins discord
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    # Creates a list of servers the bot is connected to
    servers = '\n - '.join([guild.name for guild in client.guilds])
    print(f'Servers Connected:\n - {servers}')
    create_directories()


@client.event
async def on_message(message):
    # Sends help_block to the channel it was invoked in
    if message.content == '$help':
        if message.author == client.user:
            return
        await message.channel.send(help_block)

    # Sends about_string to the channel it was invoked in
    if message.content == '$about':
        if message.author == client.user:
            return
        await message.channel.send(about_string)
        await message.channel.send(supported_hashes_s)

    # $hash command
    if '$hash' in message.content:
        if message.author == client.user:
            return

        print(str(datetime.now()) + " - $hash Command Invoked!")
        if not message.attachments:
            await message.channel.send("```Error: No file attached to message.```")
            await message.channel.send(help_block)
            return

        # Catches the user not inputting a hash name
        try:
            hashname = message.content.split()[1]
        except IndexError:
            await message.channel.send("```Error: No hash name after $hash command call.```")
            await message.channel.send(help_block)
            return

        # Checks if the hash name is valid
        if not validate_input(hashname):
            await message.channel.send("```Error: Unsupported hash entered or incorrect hash name.```")
            await message.channel.send(supported_hashes_s)
            return

        # Everything below occurs only if a file is attached and the hash name is valid
        print(message.attachments[0])
        # Saves the file to temp directory
        save_to_temp(message.attachments[0].url, message.attachments[0].id, message.attachments[0].filename)

        # Hashing the file
        fhash = hash_file(f"{message.attachments[0].id}-{message.attachments[0].filename}", hashname)

        # Prints the results of the hash and other information
        await message.channel.send(f"```Filename: {message.attachments[0].filename}```")
        await message.channel.send(f"```FileID: {message.attachments[0].id}```")
        await message.channel.send(f"```{hashname}: {fhash}```")

        # Writes information into logs.txt
        write_log(message.attachments[0], hashname + " : " + fhash, message.author.id)

        # Deletes the file from the temp folder
        delete_file(f"{message.attachments[0].id}-{message.attachments[0].filename}")

client.run(TOKEN)
