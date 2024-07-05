import asyncio
from interactions import Client, Intents, SlashContext, OptionType, listen, slash_command, slash_option, GuildCategory
from interactions.api.events import MemberAdd
import json

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

# Function to sync channels and users data
async def sync_data(guild):
    print("Syncing data...")
    data = load_data()
    channels_data = data.get("categories", {})
    user_data = data.get("users", {})
    username_to_user_id = {username.lower(): user_id for user_id, username in user_data.items()}

    # Fetch all channels
    print("Fetching channels...")
    channels = await guild.fetch_channels()
    print(f"Fetched {len(channels)} channels.\n")

    print(f"Channel data: {channels}\n")
    
    print("Processing channels...\n")
    for channel in channels:
        print(f"    Processing channel '{channel.name}'...")
        if isinstance(channel, GuildCategory):
            print(f"        Processing category '{channel.name}'...")            
            # turn the category which is a username into the user_id of that user
            potential_username = str(channel.name)
            print(f"            `potential_username`: {potential_username}")
            print(f"            `user_data`: {username_to_user_id}")
            if potential_username in username_to_user_id:
                username = potential_username
                print(f"                verified username '{username}'")
                user_id = username_to_user_id[username]
                print(f"                verified user_id '{user_id}'")
                if user_id not in channels_data:
                    channels_data[user_id] = {
                        "category_id": str(channel.id),
                        "channels": {}
                    }
                for sub_channel in channels:
                    if sub_channel.parent_id == channel.id:
                        print(f"                    Adding sub-channel '{sub_channel.name}' to user '{user_id}'...")
                        channels_data[user_id]["channels"][sub_channel.name] = {
                            "id": str(sub_channel.id),
                            "type": "public",  # Placeholder, replace with actual detection
                            "reactions": True,  # Placeholder, replace with actual detection
                            "comments": True,  # Placeholder, replace with actual detection
                            "member_ids": [],  # Placeholder, replace with actual detection
                            "roles": []  # Placeholder, replace with actual detection
                        }
            print(f"        Processed category.")
        print(f"    Processed channel.")


    # Fetch members from the guild
    print("Fetching members...")
    for member in guild.members:
        user_data[str(member.id)] = member.username
        print(f"    Added member '{member.username}' (ID: {member.id}) to user data.")

    # Save the updated data to data.json
    print("Saving data to data.json...")
    save_data({
        "users": user_data,
        "categories": channels_data
    })

    print("Sync complete.")

# `/create_channel` Slash Command
@slash_command(name="create_channel", description="Make your own private channel!")
@slash_option(
    name="name",
    description="Name of the channel",
    opt_type=OptionType.STRING,
)
async def create_channel(ctx: SlashContext, name: str):
    guild = ctx.guild

    user_id = str(ctx.author.user.id)  # Assuming ctx.author.id gives the user's Discord ID
    print(f'Creating the channel "{name}" for user_id: {user_id}...')

    print("Syncing current data for redundancy...")
    try:
        await sync_data(guild)
        print("User and Channel Data synced.")
    except Exception as e:
        print(f"Error syncing data: {e}")
        return

    # Load data.json data
    channels_data = load_data()["categories"]

    # Check if the user's entry exists in data.json
    if user_id in channels_data:
        user_data = channels_data[user_id]
        category_id = user_data["category_id"]

        # Create the channel in the user's category
        channel = await guild.create_text_channel(name=name, category=category_id)
        await ctx.send(f"Channel '{name}' created.")
        print(f"Channel '{name}' created.")
    else:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        print("No personal category found. Failed to create channel.")
    
    print("Syncing new channels data...")
    try:
        await sync_data(guild)
        print("User and Channel Data synced.")
    except Exception as e:
        print(f"Error syncing Data: {e}")

# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
