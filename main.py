from interactions import Client, Intents, SlashContext, OptionType, listen, slash_command, slash_option, GuildCategory
from interactions.api.events import MemberAdd
import json
from functools import wraps
import subprocess

bot = Client(intents=Intents.GUILD_MEMBERS | Intents.DEFAULT)

# When the discord bot is ready it will do all in this function
@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

    # Function to simulate a member join event
    '''
    async def simulate_member_add():
        from interactions.api.models.user import User
        from interactions.api.models.guild import Member

        print("Simulating member join event...")
        mock_user = User(
            username="TestUser", 
            id=1234567890, 
            discriminator="0001", 
            avatar=None, 
            bot=False, 
            system=False, 
            flags=0
        )
        mock_member = Member(
            user=mock_user, 
            roles=[], 
            joined_at=None, 
            premium_since=None, 
            deaf=False, 
            mute=False, 
            pending=False,
            guild_id=bot.guilds[0].id  # Ensure the guild_id is set in the member object
        )
        
        # Wait for the bot to properly populate its guild data
        await asyncio.sleep(2)
        if not bot.guilds:
            print("No guilds found.")
            return

        # Construct the event with the correct parameters
        event = MemberAdd(
            member=mock_member,
            guild_id=bot.guilds[0].id
        )
        
        await an_event_handler(event)
        
    await simulate_member_add()
    '''

# When Member joins
@listen(MemberAdd)
async def an_event_handler(event: MemberAdd):
    print(f"Someone joined with name: {event.member.user.username}")

    # Create a category for the new member named after their username
    category = await bot.guilds[0].create_category(name=event.member.user.username)

    # Create a channel for the new member called public in the category
    public_channel = await bot.guilds[0].create_text_channel(name="public", category=category)
    private_channel = await bot.guilds[0].create_text_channel(name="private", category=category)
    
    '''
    Send messages is off by default except the member who joined.
    View Channels is off by default except the member who joined and the public channel.
    '''
    # TODO: set permissions for category and channels

# Function to load data.json data
def load_data():
    with open('data.json', 'r') as file:
        return json.load(file)

# Function to save data.json data
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Ok this function needs a lot of work.
# It's not going to scale well because it's very un-optimized
# ^^^ especially considering how much this shit gets called
# It also does not yet have a way to see any permissions which is vital
# if two people have the same username this breaks
# if you want to make any category ever you give someone with the username of that category access, like if someone had the username: archive
def sync_data_before_and_after(func):

    # Function to sync channels and users data
    async def sync_data(guild):
        print("Syncing data...")
        pdata = load_data() # previous data
        pchannels_data = pdata.get("categories", {})
        puser_data = pdata.get("users", {})
        username_to_user_id = {username.lower(): user_id for user_id, username in puser_data.items()}

        # Fetch all channels
        print("Fetching channels...")
        channels = await guild.fetch_channels()
        print(f"Fetched {len(channels)} channels.\n")

        def process_category(channel, channels, pchannels_data, username_to_user_id):
            print(f"        Processing category '{channel.name}'...")
            potential_username = str(channel.name).lower()
            print(f"            `potential_username`: {potential_username}")
            print(f"            `username_to_user_id`: {username_to_user_id}")

            user_id = username_to_user_id.get(potential_username)
            if user_id:
                print(f"                verified user_id '{user_id}' for username '{potential_username}'")
                if user_id not in pchannels_data:
                    pchannels_data[user_id] = {
                        "category_id": str(channel.id),
                        "channels": {}
                    }
                for sub_channel in channels:
                    if sub_channel.parent_id == channel.id:
                        print(f"                    Adding sub-channel '{sub_channel.name}' to user '{user_id}'...")
                        pchannels_data[user_id]["channels"][sub_channel.name] = {
                            "id": str(sub_channel.id),
                            "type": "public",  # Placeholder, replace with actual detection
                            "reactions": True,  # Placeholder, replace with actual detection
                            "comments": True,  # Placeholder, replace with actual detection
                            "member_ids": [],  # Placeholder, replace with actual detection
                            "roles": []  # Placeholder, replace with actual detection
                        } # updating previous channel data to new data
            else:
                print(f"                No user found for category '{channel.name}'")

        print("Processing channels...\n")
        for channel in channels:
            print(f"    Processing channel '{channel.name}'...")
            if isinstance(channel, GuildCategory):
                process_category(channel, channels, pchannels_data, username_to_user_id)
            print(f"    Processed channel.\n")

        # Fetch members from the guild
        print("Fetching members...")
        for member in guild.members:
            puser_data[str(member.id)] = member.username # updating previous user data to new data
            print(f"    Added member '{member.username}' (ID: {member.id}) to user data.")

        # Save the updated data to data.json
        print("Saving data to data.json...")
        save_data({
            "users": puser_data,
            "categories": pchannels_data
        })

    @wraps(func)  # Ensure the function metadata is preserved
    async def wrapper(ctx, *args, **kwargs):
        guild = ctx.guild
        print("Syncing current data for redundancy...")
        try:
            await sync_data(guild)
            print("User and Channel Data synced.")
        except Exception as e:
            print(f"Error syncing data: {e}")
            return

        # Pass all received arguments and keyword arguments to the wrapped function
        try:
            result = await func(ctx, *args, **kwargs)
        except TypeError as e:
            print(f"Error calling {func.__name__}: {e}")
            return

        print("Syncing new channels data...")
        try:
            await sync_data(guild)
            print("User and Channel Data synced.")
        except Exception as e:
            print(f"Error syncing Data: {e}")

        return result
    return wrapper

# Helper function to call the Rust script
def generate_rss_item(title: str, content: str) -> str:
    result = subprocess.run(
        ["./rust-rss"],  # Make sure to replace with your actual Rust executable
        input=f"{title}\n{content}\n",  # Pass title and content as input
        text=True,
        capture_output=True
    )
    return result.stdout

import interactions

# `@slash_command` decorator is used to register a slash command
@slash_command(
    name="generate_rss",
    description="Generate an RSS feed from channel messages"
)
@slash_option(
    name="channel_id",
    description="Select the channel ID to generate RSS feed from",
    opt_type=OptionType.STRING,  # Accept as string to avoid integer limitations
    required=True
)
async def generate_rss(ctx: SlashContext, channel_id: str):
    guild = ctx.guild

    try:
        channel_id_int = int(channel_id)  # Convert to integer
    except ValueError:
        await ctx.send("Invalid channel ID. Please provide a valid channel ID.", ephemeral=True)
        return

    channel = guild.get_channel(channel_id_int)

    # Ensure the selected channel exists and is a text channel
    if not channel or channel.type != interactions.ChannelType.GUILD_TEXT:
        await ctx.send("Please select a valid text channel.", ephemeral=True)
        return

    # Fetch messages from the selected channel
    messages = await channel.history(limit=100).flatten()  # Adjust the limit as needed

    # Initialize RSS feed items list
    rss_items = []

    for message in messages:
        # Skip messages without content
        if not message.content:
            continue

        title = f"Message by {message.author.username} on {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        content = message.content

        # Generate RSS item using the Rust script
        rss_item = generate_rss_item(title, content)
        rss_items.append(rss_item)

    # Create the full RSS feed
    rss_feed = "\n".join(rss_items)

    # Save the RSS feed to a file
    with open("feed.xml", "w") as file:
        file.write(rss_feed)

    await ctx.send("RSS feed generated successfully!", ephemeral=True)



# `/create_channel` command
@slash_command(name="create_channel", description="Make your own private channel!")
@slash_option(name="name", description="Name of the channel", opt_type=OptionType.STRING)
@sync_data_before_and_after
async def create_channel(ctx: SlashContext, name: str):
    guild = ctx.guild
    user_id = str(ctx.author.user.id)
    data = load_data()
    channels_data = data["categories"]
    user_data = channels_data.get(user_id)
    if not user_data:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        return

    category_id = user_data["category_id"]
    channel = await guild.create_text_channel(name=name, category=category_id)
    await ctx.send(f"Channel '{name}' created.")

# `/rename_channel` command
@slash_command(name="rename_channel", description="Rename one of your channels")
@slash_option(name="old_name", description="Current name of the channel to rename", opt_type=OptionType.STRING)
@slash_option(name="new_name", description="New name for the channel", opt_type=OptionType.STRING)
@sync_data_before_and_after
async def rename_channel(ctx: SlashContext, old_name: str, new_name: str):
    guild = ctx.guild
    user_id = str(ctx.author.user.id)
    data = load_data()
    channels_data = data["categories"]
    user_data = channels_data.get(user_id)
    if not user_data:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        return
    
    if old_name not in user_data["channels"]:
        await ctx.send(f"Channel '{old_name}' not found.")
        return

    old_channel_id = user_data["channels"][old_name]["id"]
    old_channel = guild.get_channel(int(old_channel_id))
    if not old_channel:
        await ctx.send(f"Channel '{old_name}' not found in the server.")
        return

    # Update data and server channel
    try:
        await old_channel.edit(name=new_name)
    except Exception as e:
        await ctx.send(f"Error renaming channel: {e}")
        return

    # Update data in memory
    user_data["channels"][new_name] = user_data["channels"].pop(old_name)
    await ctx.send(f"Channel '{old_name}' renamed to '{new_name}'.")

# TODO: this deletes the channels completely rather than moving them to the archive category

# `/delete_channel` command
@slash_command(name="delete_channel", description="Delete one of your channels")
@slash_option(name="name", description="Name of the channel to delete", opt_type=OptionType.STRING)
@sync_data_before_and_after
async def delete_channel(ctx: SlashContext, name: str):
    guild = ctx.guild
    user_id = str(ctx.author.user.id)
    data = load_data()
    channels_data = data["categories"]
    user_data = channels_data.get(user_id)
    if not user_data:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        return
    
    if name not in user_data["channels"]:
        await ctx.send(f"Channel '{name}' not found.")
        return

    channel_id = user_data["channels"][name]["id"]
    channel = guild.get_channel(int(channel_id))
    if not channel:
        await ctx.send(f"Channel '{name}' not found in the server.")
        return

    # Delete channel from server
    try:
        await channel.delete()
    except Exception as e:
        await ctx.send(f"Error deleting channel: {e}")
        return

    # Update data in memory
    user_data["channels"].pop(name)
    await ctx.send(f"Channel '{name}' deleted.")

# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
