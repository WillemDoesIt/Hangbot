from interactions import Client, Intents, SlashContext, OptionType, listen, slash_command, slash_option, GuildCategory, Permissions, PermissionOverwrite, OverwriteType, Member
import interactions
from interactions.api.events import MemberAdd
import json
from functools import wraps
import subprocess
import asyncio

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
        if not bot.guilds:
            print("No guilds found.")
            return

        guild = bot.guilds[0]

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
            guild_id=guild.id  # Ensure the guild_id is set in the member object
        )
        
        # Construct the event with the correct parameters
        event = MemberAdd(
            member=mock_member,
            guild_id=guild.id
        )
        await on_member_join(event)

    await simulate_member_add()
    '''

@listen(MemberAdd)
async def on_member_join(event: MemberAdd):
    print(f"Someone joined with name: {event.member.user.username}")

    guild = bot.guilds[0]

    # Create a category for the new member named after their username
    category = await guild.create_category(name=event.member.user.username)

    # Create channels for the new member in the category
    public_channel = await guild.create_text_channel(name="public", category=category)
    private_channel = await guild.create_text_channel(name="private", category=category)

    # Deny everyone else the ability to view and send messages
    await category.set_permission(target=guild.default_role, view_channel=False, send_messages=False)
    await public_channel.set_permission(target=guild.default_role, view_channel=False, send_messages=False)
    await private_channel.set_permission(target=guild.default_role, view_channel=False, send_messages=False)

    # TODO: Iterate through every member of the server and block them from viewing the private channel

    # Ensure the target is a Member type
    member = event.member
    if isinstance(member, interactions.Member):
        await category.set_permission(target=member, view_channel=True, send_messages=True)
        await public_channel.set_permission(target=member, view_channel=True, send_messages=True)
        await private_channel.set_permission(target=member, view_channel=True, send_messages=True)
    else:
        print("Error: event.member is not a Member instance")
    # Log the creation of the category and channels
    log_channel = bot.get_channel(1269023924415627335)  # Replace with your log channel ID
    await log_channel.send(f"Created category and channels for {event.member.user.username}.")


def fetch_user_category(func):
    @wraps(func)
    async def wrapper(ctx: SlashContext, *args, **kwargs):
        guild = ctx.guild
        category_name = ctx.author.user.username  # Using the username as the category name

        # Fetch all categories and find the user's category
        categories = await guild.fetch_channels()
        user_category = None
        for category in categories:
            if isinstance(category, GuildCategory) and category.name.lower() == category_name.lower():
                user_category = category
                break

        if not user_category:
            await ctx.send("No personal category found. Please contact staff to troubleshoot.")
            return

        return await func(ctx, user_category, *args, **kwargs)
    return wrapper

def fetch_channel(func):
    @wraps(func)
    async def wrapper(ctx: SlashContext, user_category: GuildCategory, *args, **kwargs):
        # Determine the channel name based on the function's expected parameters
        channel_name = kwargs.get('name') or kwargs.get('old_name')  # Prefer kwargs over args
        if not channel_name:
            await ctx.send("Channel name not provided.")
            return

        # Find the channel in the user's category
        channel = None
        for ch in user_category.channels:
            if ch.name.lower() == channel_name.lower():
                channel = ch
                break

        if not channel:
            await ctx.send(f"Channel '{channel_name}' not found.")
            return

        return await func(ctx, user_category, channel, *args, **kwargs)
    return wrapper

@slash_command(name="create_channel", description="Make your own private channel!")
@slash_option(name="name", description="Name of the channel", opt_type=OptionType.STRING)
@fetch_user_category
async def create_channel(ctx: SlashContext, user_category: GuildCategory, name: str):
    guild = ctx.guild
    # Create the channel in the user's category
    channel = await guild.create_text_channel(name=name, category=user_category)
    await ctx.send(f"Channel '{name}' created.")

@slash_command(name="rename_channel", description="Rename one of your channels")
@slash_option(name="old_name", description="Current name of the channel to rename", opt_type=OptionType.STRING)
@slash_option(name="new_name", description="New name for the channel", opt_type=OptionType.STRING)
@fetch_user_category
@fetch_channel
async def rename_channel(ctx: SlashContext, user_category: GuildCategory, channel, old_name: str, new_name: str):
    try:
        await channel.edit(name=new_name)
        await ctx.send(f"Channel '{old_name}' renamed to '{new_name}'.")
    except Exception as e:
        await ctx.send(f"Error renaming channel: {e}")

@slash_command(name="delete_channel", description="Delete one of your channels")
@slash_option(name="name", description="Name of the channel to delete", opt_type=OptionType.STRING)
@fetch_user_category
@fetch_channel
async def delete_channel(ctx: SlashContext, user_category: GuildCategory, channel, name: str):
    try:
        await channel.delete()
        await ctx.send(f"Channel '{name}' deleted.")
    except Exception as e:
        await ctx.send(f"Error deleting channel: {e}")

@slash_command(name="block", description="Block a user from accessing your channels")
@slash_option(
    name="user",
    description="",
    required=True,
    opt_type=OptionType.USER,
)
@fetch_user_category
async def block_user(ctx: SlashContext, user_category: GuildCategory, user:OptionType.USER=None):
    member = await ctx.guild.fetch_member(user.id)
    await user_category.set_permission(target=member, view_channel=False, send_messages=False)
    await ctx.send(f"User '{user.username}' has been blocked from your channels.")

@slash_command(name="unblock", description="Unblock a user from accessing your channels")
@slash_option(
    name="user",
    description="",
    required=True,
    opt_type=OptionType.USER,
)
@fetch_user_category
async def unblock_user(ctx: SlashContext, user_category: GuildCategory, user:OptionType.USER=None):
    member = await ctx.guild.fetch_member(user.id)
    await user_category.set_permission(target=member, view_channel=True, send_messages=True)
    await ctx.send(f"User '{user.username}' has been unblocked and granted access to your channels.")

@slash_command(name="list_blocked", description="List all users blocked from accessing your channels")
@fetch_user_category
async def list_blocked(ctx: SlashContext, user_category: GuildCategory):
    blocked_users = []

    # Get all permission overwrites for the category
    permissions = user_category.permission_overwrites

    for overwrite in permissions:
        if not overwrite.allow & Permissions.VIEW_CHANNEL and not overwrite.allow & Permissions.SEND_MESSAGES:
            try:
                blocked_user = await ctx.guild.fetch_member(overwrite.id)
                if blocked_user:
                    blocked_users.append(blocked_user.user.username)
            except Exception as e:
                print(f"Error fetching member: {e}")

    if not blocked_users:
        await ctx.send("You have not blocked any users.")
    else:
        blocked_users_str = ", ".join(blocked_users)
        await ctx.send(f"Blocked users: {blocked_users_str}")

@slash_command(name="follow", description="Follow a users category to have it appear")
@slash_option(
    name="user",
    description="",
    required=True,
    opt_type=OptionType.USER,
)
async def follow(ctx: SlashContext, user:OptionType.USER=None):
    guild = ctx.guild 
    category_name = user.username  # Using the username as the category name

    # Fetch all categories
    categories = await guild.fetch_channels()
    user_category = None
    
    for category in categories:
        if isinstance(category, GuildCategory) and category.name.lower() == category_name.lower():
            user_category = category
            break

    if user_category is None:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        return

    member = await ctx.guild.fetch_member(user.id)
    await user_category.set_permission(target=ctx.author, view_channel=True)
    await ctx.send(f"You are now following '{user.username}'")

@slash_command(name="unfollow", description="Unfollow a user's category to have it disappear")
@slash_option(
    name="user",
    description="The user whose category you want to unfollow",
    required=True,
    opt_type=OptionType.USER,
)
async def unfollow(ctx: SlashContext, user: OptionType.USER=None):
    guild = ctx.guild 
    category_name = user.username  # Using the username as the category name

    # Fetch all categories
    categories = await guild.fetch_channels()
    user_category = None
    
    for category in categories:
        if isinstance(category, GuildCategory) and category.name.lower() == category_name.lower():
            user_category = category
            break

    if user_category is None:
        await ctx.send("No personal category found. Please contact staff to troubleshoot.")
        return

    await user_category.set_permission(target=ctx.author, view_channel=False)
    await ctx.send(f"You are now unfollowing '{user.username}'")



# Run the bot using the token from token.json
PATH = "token.json"
with open(PATH, 'r') as tokenFile:
    token = json.load(tokenFile)
bot.start(token["token1"])
