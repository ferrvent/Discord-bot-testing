import discord # Imports Discord's personal library into the code
import re # Imports re, used for the ban command
import asyncio # Imports asyncio, also used for the ban command
from discord.ext import commands # This is for commands
from discord import app_commands # This is also for commands

GUILD = discord.Object(id=Insert your Discord server's ID) # Creates a GUILD variable so you don't have to type the ID every time

class Client(commands.Bot): # Creates a client for you to put your first few commands in
    async def on_ready(self): # Prints a message whenever the bot is launched
        print(f'Logged on as {self.user}')
        try:
            synced = await self.tree.sync(guild=GUILD)
            print(f'Synced {len(synced)} command/s to guild {GUILD.id}')
        except Exception as e:
            print(f'Sync failed: {e}')

    async def on_message(self, message): # Makes the bot reply whenever someone types "hello" in their message with that specific capitalization
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author}')


intents = discord.Intents.default() # Sets the intents, you have to turn all 3 intents on in your bot for this to work
intents.message_content = True # Turns on a setting within your intents

client = Client(command_prefix="$", intents=intents) # Sets a "client" variable used for making commands

class Menu(discord.ui.Select): # Creates the buttons and base for a dropdown menu used later on in a command
    def __init__(self):
        options1 = [ # Fancy way of separating each option, you can do it in a messy way but I prefer this
            discord.SelectOption(
                label="Option 1", # The label is just a cool way of saying "This is a title"
                description="This is the 1st option", # The description is well, a description
                emoji="1️⃣" # Cool emoji :D
                # Final display looks a little something like this: 
            ),
            # Everything below is exactly the same as above, just different labels, descriptions and emojis
            discord.SelectOption(
                label="Option 2",
                description="This is the 2nd option",
                emoji="2️⃣"
            ),
            discord.SelectOption(
                label="Option 3",
                description="This is the 3rd option",
                emoji="3️⃣"
            )
        ]

        super().__init__(placeholder="Click here to choose an option!", min_values=1, max_values=1, options=options1) # This is very important, it's the base of the actual dropdown menu and specifies the minimum amount of buttons you can press
      # at a time and maximum, it also tells it what options to use which are just the "options1" ones that we created above

    async def callback(self, interaction: discord.Interaction): # This is just whatever happens when you press one of the buttons in the dropdown menu above
        try:
            await interaction.response.send_message(f'You have chosen {self.values[0]}!', ephemeral=True)
        except Exception as e:
            print(f'An error occured while attempting Dropdown callback: {e}')

class MenuView(discord.ui.View): # This is to make the dropdown menu visible when you use the command I think; I'm not sure what it specifically does
    def __init__(self):
        super().__init__()
        self.add_item(Menu())


class ButtonView(discord.ui.View): # This is creates a button and also adds the callback for it, as I call it, which is what happens you press that button
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.red, emoji="🥹")
    async def button_callback(self, button, interaction):
        await button.response.send_message("Yay, you clicked me!", ephemeral=True)



@client.tree.command(name="hello", description="Make the bot say hello!", guild=GUILD) # Pretty self explanatory, it's a command that makes the bot say "Hey there!"
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hey there!")

@client.tree.command(name="printer", description="Print a message.", guild=GUILD) # Makes the bot print out whatever message you want it to
async def printer(interaction: discord.Interaction, printer: str, the_channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    await the_channel.send(printer)
    await interaction.followup.send(f"Sent to {the_channel.mention}", ephemeral=True)

@client.tree.command(name="imgprinter", description="Print an image.", guild=GUILD) # Makes the bot print out whatever image you want it to
async def imgprinter(interaction: discord.Interaction, pictureprinter: discord.Attachment, channel2: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    await channel2.send(pictureprinter)
    await interaction.followup.send(f"Sent your stinky image to {channel2.mention}")

@client.tree.command(name="embedtest", description="Testing embeds", guild=GUILD) # Random embed test thingy
async def embed(interaction: discord.Interaction):
    try:
        embed = discord.Embed(title="This is a title.", description="This is a description (maybe)") # This is your embed's title and description
        embed.set_image(url="Insert an image ID here") # This is your embed's image
        embed.add_field(name="This may or may not be a field >:D", value="Shut the fuck up liar") # This is a field which is basically like a section in an embed
        await interaction.response.send_message(embed=embed, view=MenuView()) # This basically just tells the code that the embed it should use is called "embed" which is what we specified above for the discord interaction, and that the "view" aka the button or dropdopdown menu is called MenuView (which we set above)
    except Exception as e: # This is supposed to print out a message if something goes wrong or unaccording to the code above
        print(f'Failed to execute embedtest, {e}')


@client.tree.command(name="ban", description="Ban a user!", guild=GUILD) # This is a ban command, obviously
async def ban(interaction: discord.Interaction, user: discord.User, reason: str, duration: str): # Sets a "user" variable for the banned user, a reason variable for the reason of the ban, and a guild variable for the discord server it happens in (used for efficiency)
    try:
        def parse_duration(duration: str) -> int: # This whole portion basically uses the re library to make it so the user can type "1s" or "10m" and so on to specify the ban duration instead of typing it in a set variable like seconds, minutes, or hours
            match = re.fullmatch(r"(\d+)([smhd])", duration.lower())
            if not match:
                print(f"Ban command has been attempted.")
            amount, unit = match.groups()
            amount = int(amount)
            if unit == "s":
                return amount
            elif unit == "m":
                return amount * 60
            elif unit == "h":
                return amount * 3600
            elif unit == "d":
                return amount * 86400
        seconds = parse_duration(duration)
        await user.send(f"You have been banned from the server!") # Sends a message to the banned user telling them they were banned
        blg = interaction.guild.get_channel(Whatever logs channel you want lol) # Sets a log channel for the ban message to be sent in
        if blg: # If the logs channel you set actually exists:
            await blg.send(f"{user.mention} has been banned for {duration}!") # Actually sends the message saying that user is now banned
        else: # If something goes wrong with specifically the logging process:
            print(f"Unsuccessfully logged a recent ban: {e}") # Prints the error
        await interaction.guild.ban(user, reason=reason) # Bans the user
        await interaction.response.send_message(f"Successfully banned {user.mention} for {duration}!") # Sends a message in the channel the user was banned in
        await asyncio.sleep(seconds) # Uses the asyncio library for the ban duration, I'm too lazy to do it otherwise
        await interaction.guild.unban(user) # Unbans the user after the ban duration is over
    except Exception as e: # If something goes wrong with the whole ban command:
        print(f"An error has recently occured while banning a user: {e}") # Prints an error
        # Everything below is already explained above, I just copy-pasted all of it again because it wouldn't work otherwise for some reason
        blg = interaction.guild.get_channel(Insert the ID of your logs channel)
        if blg:
            await blg.send(f"{user.mention} has been banned for {duration}!")
        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"Successfully banned {user.mention} for {duration}!")
        await asyncio.sleep(seconds)
        await interaction.guild.unban(user)




@client.tree.command(name="buttontest", description="Testing buttons", guild=GUILD) # The button I talked about earlier
async def button1(interaction: discord.Interaction):
    await interaction.response.send_message(view=ButtonView()) # Sends a message and tells the bot that it wants the view to be ButtonView this time instead of the MenuView one above

client.run("Insert your Discord bot's token")
