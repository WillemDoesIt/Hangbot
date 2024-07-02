from interactions import Client, Intents, listen, slash_command
from interactions.api.events import MemberAdd 
import json

bot = Client(intents=Intents.DEFAULT)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

# TODO: When a player joins for the first time we need it to detect that, it shouldn't trigger on rejoins
# The current implementation may work but I'm not certain, it doesn't seem to trigger on rejoins, but it also doesn't seem to trigger at all
@listen(MemberAdd)
async def an_event_handler(event: MemberAdd):
    print(f"Someone joined with name: ")

@slash_command(name='ping')
async def ping(ctx):
    await ctx.send('Pong')

# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
