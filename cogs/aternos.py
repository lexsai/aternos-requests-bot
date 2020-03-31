import random
import aiohttp
import string
import datetime
import websockets

import discord
from discord.ext import commands

class Aternos(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.x = self.generate_random_string()
        self.y = self.generate_random_string()

    def generate_random_string(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

    async def manage_queue(self, session, aternos_session):
        header = ('Cookie', f'ATERNOS_SESSION={aternos_session}')
        async with websockets.connect('wss://aternos.org/hermes/', extra_headers=[header]) as websocket:
            while True:
                msg = await websocket.recv()
                print(msg)
                if 'pending' in msg:
                    await self._confirm(session)
                    break

                elif 'starting' in msg:
                    print('okok')
                    break

    async def _confirm(self, session):
        r = await session.request('get',
                                  'https://aternos.org/panel/ajax/confirm.php',
                                   params = {'ASEC':f'{self.x}:{self.y}'})

        print('[CONFIRM]', r.status, r.reason, await r.text())       
        return r        

    async def _login(self, session, data):
#        data = {
#            'user' : 'exampleaccount123123',
#            'password' : 'e99a18c428cb38d5f260853678922e03'
#        }

        r = await session.request('post',
                                  'https://aternos.org/panel/ajax/account/login.php',
                                   data = data,
                                   params = {"ASEC":f"{self.x}:{self.y}"})

        print('[LOGIN]', r.status, r.reason, await r.text())       
        return r

    async def _start(self, session):
        r = await session.request('get',
                                  'https://aternos.org/panel/ajax/start.php',
                                   params = {'headstart' : 0, 
                                             'ASEC':f'{self.x}:{self.y}'})

        print('[START]', r.status, r.reason, await r.text())       
        return r

    async def _stop(self, session):
        r = await session.request('get',
                                  'https://aternos.org/panel/ajax/stop.php',
                                   params = {'ASEC':f'{self.x}:{self.y}'})

        print('[STOP]', r.status, r.reason, await r.text())       
        return r        

    async def get_login(self, ctx):        
        embed = discord.Embed(title=f'Please check your DMs.',
                              description=f'{ctx.author.mention}', 
                              colour=discord.Colour(0x79c496)) 
        temp_message = await ctx.send(embed=embed)
        await temp_message.delete(delay=5)

        embed = discord.Embed(title='LOGIN:', 
                              description='Please send your login details, in format:\n```<username>\n<password>```',
                              colour=discord.Colour(0x79c496)) 
        await ctx.author.send(embed=embed)

        credential_msg = await ctx.bot.wait_for('message', check = lambda m: m.guild == None and m.author.id == ctx.author.id, timeout=60)
        
        credentials = dict(zip(['user', 'password'], credential_msg.content.split('\n')))
        
        await ctx.author.send(f'Thank you, return to {ctx.channel.mention}.')

        print(credentials)
        return credentials

    @commands.command()
    async def start(self, ctx):
        print('STARTING:')

        cookie = {f'ATERNOS_SEC_{self.x}' : self.y}
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

        credentials = await self.get_login(ctx)

        async with aiohttp.ClientSession(cookies=cookie, headers=headers) as session:
            await self._login(session, credentials)
            r = await self._start(session)

            if 'already' in await r.text():
                embed = discord.Embed(title='Aternos server already started.', 
                                      timestamp=datetime.datetime.now(),    
                                      colour=discord.Colour(0x79c496)) 
                msg = await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title='Aternos server entering queue.', 
                                      timestamp=datetime.datetime.now(),    
                                      colour=discord.Colour(0x79c496)) 
                msg = await ctx.send(embed=embed)
                
                await self.manage_queue(session, r.cookies['ATERNOS_SESSION'].value)

                embed = discord.Embed(title='Aternos server starting..', 
                                      timestamp=datetime.datetime.now(),    
                                      colour=discord.Colour(0x79c496)) 
                await msg.edit(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        print('STOPPING:')

        cookie = {f'ATERNOS_SEC_{self.x}' : self.y}
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

        credentials = await self.get_login(ctx)

        async with aiohttp.ClientSession(cookies=cookie, headers=headers) as session:
            await self._login(session, credentials)  
            await self._stop(session)

        embed = discord.Embed(title='Aternos server stopped.', 
                              timestamp=datetime.datetime.now(),    
                              colour=discord.Colour(0x79c496)) 

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Aternos(bot))