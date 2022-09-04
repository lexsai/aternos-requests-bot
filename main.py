import os
import traceback

import discord
from discord.ext import commands

class AternosBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        extensions = sorted([f"cogs.{os.path.splitext(cog)[0]}" for cog in os.listdir("cogs") if os.path.splitext(cog)[1] == '.py'])   
        self.load_extensions(extensions)

    async def on_ready(self):
        print('-')
        print(f'Logged in as "{self.user.name}" - User ID : {self.user.id}')
        print(f'Command Prefix: {self.command_prefix}')
        print('-')

    def load_extensions(self, extensions):
        print("Loading extensions:")
        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"\"{extension}\" loaded. ({extensions.index(extension)+1}/{len(extensions)})")
            except:
                print(f"Failed to load extension {extension}.")
                traceback.print_exc()

if __name__ == '__main__':
    bot = AternosBot(command_prefix='>')
    bot.run('...')


