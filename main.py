import asyncio
from interactions import Client, Intents, SlashContext, OptionType, listen, slash_command, slash_option
from interactions.api.events import MemberAdd
import json

bot = Client(intents=Intents.GUILD_MEMBERS | Intents.DEFAULT)

# Function to load and save channels.json data
def sync_channels_data(channels_data):
    #TODO: make this work

    pass

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

# Load channels.json data
def load_channels_data():
    with open('channels.json', 'r') as f:
        return json.load(f)

# `/create_channel` Slash Command
@slash_command(name="create_channel", description="Make your own private channel!")
@slash_option(
    name="name",
    description="Name of the channel",
    opt_type=OptionType.STRING,
)
async def create_channel(ctx: SlashContext, name: str):
    sync_channels_data()

    guild = ctx.guild
    username = str(ctx.author.username)  # Assuming ctx.author.id gives the user's Discord ID
    print(f"Username: {username}")

    # Load channels.json data
    channels_data = load_channels_data()
    print(f"Channels data: {channels_data}")

    # Check if the user's entry exists in channels.json
    if username in channels_data:
        user_data = channels_data[username]
        print(f"User data: {user_data}")
        category_id = user_data["category_id"]

        # Create the channel in the user's category
        channel = await guild.create_text_channel(name=name, category=category_id)
        await ctx.send(f"Channel '{name}' created successfully!")
    else:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
    
    sync_channels_data()

# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
