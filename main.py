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
    channels_data = load_data()["categories"]
    user_data = load_data()["users"]

    # Fetch all channels
    channels = await guild.fetch_channels()
    
    for channel in channels:
        if isinstance(channel, GuildCategory):
            category = channel.category
            if category:
                user_id = category.name.lower()  # Assuming category name is the user_id
                if user_id in channels_data:
                    if channel.name not in channels_data[user_id]["channels"]:
                        # Initialize channel data
                        channels_data[user_id]["channels"][channel.name] = {
                            "id": str(channel.id),
                            "type": "public", # TODO: find how to detect public vs private
                            "reactions": True, # TODO: find how to detect if reactions are enabled
                            "comments": True, # TODO: find how to detect if comments are enabled
                            "member_ids": [], # TODO: find how to detect member ids
                            "roles": [] # TODO: find how to detect roles
                        }
                else:
                    # Create a new entry for this user's category if it doesn't exist
                    channels_data[user_id] = {
                        "category_id": str(category.id),
                        "channels": {}
                    }
 
    # Use guild.members to get the cached member list
    for member in guild.members:
        user_data[str(member.id)] = member.display_name

    # Save the updated data to data.json
    save_data({
        "users": user_data,
        "categories": channels_data
    })

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
