# HangBot

The goal of this project is to create a fully functional social media platform through discord. Specifically one that will work well with the small web / personal movement.

## Current Version beta 1.0
 - On join a category is created in your username.
   - a public channel is created
   - a private channel is created

despite the name private channels are not yet private.


## End Goal
On join you are given a Personal category and a Public and Private channel (feed) that you can write messages in. No one else can write in your channels.

You use commands like `/create_channel`, `/rename_channel`, `/delete_channel` to manage your channels. To configure them further you may use `/permissions` to control who can view them, if people can comment or react.

To view other peoples channels you may follow them `/follow`, this adds there category to your channel view list, allowing you to see their public channels, they can choose weather or not to show you private channels through `/permissions`. This also means to not over-bloat your channel list you can `/unfollow` others

You can turn your public channels into RSS feeds
I'm not sure if this would work yet but I think I could do some kind of token based authentication and discord side management to allow for private RSS as well where it's synced with who can view. But I'm not certain about that yet.

There are some ideas I have around profiles and linking personal websites through that but I'm not sure about that either. But the RSS will be something you can turn into html and embed into your website. I have a js script that already does this already, I'll link it later

TODO: come up with what the permissions system should look like
TODO: research private rss feeds more
TODO: come up with a profile system
TODO: link the js code in the README