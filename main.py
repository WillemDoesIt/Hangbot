import asyncio
from interactions import Client, Intents, listen, slash_command
from interactions.api.events import MemberAdd
import json

bot = Client(intents=Intents.GUILD_MEMBERS | Intents.DEFAULT)

@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

    # Function to simulate a member join event
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

@listen(MemberAdd)
async def an_event_handler(event: MemberAdd):
    print(f"Someone joined with name: {event.member.user.username}")
    # Create a category for the new member named after then
    

@slash_command(name='ping')
async def ping(ctx):
    await ctx.send('Pong')

# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
