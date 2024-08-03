# Introduction
At HangSpace, in collaboration with ImoNet hosting for our Discord bot HangBot, we are committed to protecting our users privacy. Our privacy policy outlines how we manage and protect user data while ensuring our TOS through moderation.

# Personal Channels
Your "Public" channels are visible to anyone who follows them, and they are always visible to moderators and administrators by default.

"Private" channels give you control over access. You and the server owner will always be able to see your private channel. This is a limitation of Discord's design, not a policy choice. If you provide access to the channel to anyone then that means there is a chance for user interaction and we must also give the rest of the moderation staff access to your private channel.

Any unauthorized sharing of private channel content from users or staff will result in message deletion, the staff to be demoted or user to get a warning. Learn about our warning system in the TOS.

# RSS System
All Public channels are hosted on ImoNet as RSS feeds and are accessible to anyone. The URL of your RSS feed is not disclosed to the public, only accessible to you and your followers.

Private RSS feeds are also hosted through ImoNet but use a token system to restrict access. 

### Token System
For example:
`imonet.com/feeds/8583927573928.xml?token=9234498327927`
The feed is only accessible with a valid token. Tokens are generated from salted hashes of the viewer's username.

While it is technically possible for someone to leak your private feed, the token would also grant access to their own feeds. Hence, leaking a private feed involves exposing one's own feed as well. Any evidence of someone doing this results in an immediate ban.

### Encrypted by default

All Private RSS feeds are encrypted and are only unencrypted by the token.

HangSpace Staff and Moderators do not have access to the RSS files, ImoNet and the server owner only has access to the Encrypted versions of the files.

# Open Source
All of the code used is open source and visible on our Github.

The bot token and string used to salt hashes remain private.

Just because this is open source does *not* mean you are entitled to where I take this project. I will never accept requests to transfer ownership or requests for code change

# Security and Compliance
We implement robust security measures to protect your data and tokens. All practices comply with applicable privacy laws and regulations. For further details on data protection and user rights, please contact us.