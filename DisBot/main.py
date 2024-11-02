import discord
import asyncio
from discord.ext import commands
from database import initialize_db, save_template, load_template, list_templates

# Создаем экземпляр бота
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    initialize_db()
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def id(ctx):
    
    owner_id = ctx.author.id
    await ctx.send(f' ваш id:"{owner_id}"')

@bot.command()
async def channels(ctx):
    guild = ctx.guild  # Получаем текущий сервер (гильдию)
    
    # Проходим по категориям (разделам)
    for category in guild.categories:
        i = 0
        await ctx.send(f"Категория: {category.name}. Позиция: {i}")  # Отправляем название категории
        i = i + 1

        # Проходим по каналам в категории
        for channel in category.channels:
            await ctx.send(f" - Канал: {channel.name} Позиция: {channel.position}")

@bot.command()
async def save(ctx):
    guild = ctx.guild  # Получаем текущий сервер (гильдию)
    template_name = guild.name
    owner_id = ctx.author.id

    save_template(template_name, guild, owner_id)
    await ctx.send(f'Template was saved under the name "{template_name}"')

@bot.command()
async def load(ctx, *, template_name: str):
    guild = ctx.guild
    owner_id = ctx.author.id

    # Получаем все шаблоны с указанным именем
    templates = list_templates(template_name, owner_id)

    if not templates:
        await ctx.send(f'No templates found with the name "{template_name}".')
        return

    if len(templates) > 1:
        response = "Multiple templates found:\n"
        for i, template in enumerate(templates):
            response += f"{i + 1}. Template ID: {template['template_id']}, Created at: {template['data']}\n"
        await ctx.send(response + "Please reply with the template number you want to load.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(templates)

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            selected_template_index = int(msg.content) - 1
        except asyncio.TimeoutError:
            await ctx.send('You took too long to respond!')
            return
    else:
        selected_template_index = 0

    # Удаляем существующие категории и каналы перед загрузкой нового шаблона
    try:
        for category in guild.categories:
            await category.delete()
    
        for channel in guild.channels:
            await channel.delete()
            
    except Exception as e:
        await ctx.send(f'Error deleting categories: {e}')
        return

    # Загружаем выбранный шаблон
    categories, channels = load_template(templates[selected_template_index]['template_id'])

    for category in categories:
        category_name = category[2]
        try:
            new_category = await guild.create_category(category_name)

            for channel in channels:
                if channel[2] == category[0]:  # Проверяем, что канал принадлежит категории
                    channel_name = channel[3]
                    channel_type = channel[4]
                    if channel_type == "text":
                        await new_category.create_text_channel(channel_name)
                    elif channel_type == "voice":
                        await new_category.create_voice_channel(channel_name)
        except Exception as e:
            await ctx.send(f'Error creating category or channel: {e}')
            return

    await ctx.send(f'Template "{template_name}" was loaded.')

# Запуск бота
bot.run('YOUR_TOKEN')
