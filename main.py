import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_NAMES = ["연맹원", "임원", "관리자"]
NATION_ROLES = ["China", "France", "Japan", "Korea (South)", "Saudi Arabia", "United Kingdom", "United States", "Vietnam"]
VERIFIED_ROLE_NAME = "인증됨"
WELCOME_CHANNEL_NAME = "welcome-only"

user_status = {}  # user_id: {"role": bool, "nation": bool}

class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_name in ROLE_NAMES:
            self.add_item(RoleButton(role_name))

class RoleButton(discord.ui.Button):
    def __init__(self, role_name):
        super().__init__(label=role_name, style=discord.ButtonStyle.primary)
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        new_role = discord.utils.get(guild.roles, name=self.role_name)
        if not new_role:
            await interaction.response.send_message(f"'{self.role_name}' 역할이 서버에 없습니다.", ephemeral=True)
            return

        for role in user.roles:
            if role.name in ROLE_NAMES and role != new_role:
                await user.remove_roles(role)

        if new_role not in user.roles:
            await user.add_roles(new_role)

        # 기록
        if user.id not in user_status:
            user_status[user.id] = {"role": False, "nation": False}
        user_status[user.id]["role"] = True
        await try_verify_user(user)

        await interaction.response.send_message(f"'{self.role_name}' 역할이 부여되었습니다!", ephemeral=True)

class NationSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_name in NATION_ROLES:
            self.add_item(NationButton(role_name))

class NationButton(discord.ui.Button):
    def __init__(self, role_name):
        super().__init__(label=role_name, style=discord.ButtonStyle.secondary)
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        new_role = discord.utils.get(guild.roles, name=self.role_name)
        if not new_role:
            await interaction.response.send_message(f"'{self.role_name}' 역할이 서버에 없습니다.", ephemeral=True)
            return

        for role in user.roles:
            if role.name in NATION_ROLES and role != new_role:
                await user.remove_roles(role)

        if new_role not in user.roles:
            await user.add_roles(new_role)

        # 기록
        if user.id not in user_status:
            user_status[user.id] = {"role": False, "nation": False}
        user_status[user.id]["nation"] = True
        await try_verify_user(user)

        await interaction.response.send_message(f"'{self.role_name}' 국적 역할이 부여되었습니다!", ephemeral=True)

async def try_verify_user(user):
    guild = user.guild
    status = user_status.get(user.id)
    if status and status["role"] and status["nation"]:
        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        if verified_role and verified_role not in user.roles:
            await user.add_roles(verified_role)
            try:
                await user.send("국적과 역할이 모두 선택되어 '인증됨' 역할이 부여되었습니다. 서버 이용이 가능합니다!")
            except:
                pass

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"{member.mention}님 환영합니다! 아래에서 국적과 역할을 선택해주세요.")
        await channel.send("**국적을 선택하세요:**", view=NationSelectView())
        await channel.send("**역할을 선택하세요:**", view=RoleSelectView())

@bot.command()
@commands.has_permissions(administrator=True)
async def 역할버튼(ctx):
    await ctx.send("역할을 선택하세요!", view=RoleSelectView())

@bot.command()
@commands.has_permissions(administrator=True)
async def 국적버튼(ctx):
    await ctx.send("국적을 선택하세요!", view=NationSelectView())

@bot.command()
async def 권한(ctx, *, 역할: str = None):
    if 역할 is None:
        await ctx.send("아래 버튼을 눌러 본인의 역할을 선택하세요!", view=RoleSelectView())
        return

    역할 = 역할.strip()
    if 역할 not in ROLE_NAMES:
        await ctx.send(f"'{역할}'은 유효한 역할이 아닙니다. 가능한 역할: {', '.join(ROLE_NAMES)}")
        return

    guild = ctx.guild
    user = ctx.author
    new_role = discord.utils.get(guild.roles, name=역할)

    if not new_role:
        await ctx.send(f"'{역할}' 역할이 서버에 없습니다.")
        return

    for role in user.roles:
        if role.name in ROLE_NAMES and role != new_role:
            await user.remove_roles(role)

    if new_role not in user.roles:
        await user.add_roles(new_role)
        if user.id not in user_status:
            user_status[user.id] = {"role": False, "nation": False}
        user_status[user.id]["role"] = True
        await try_verify_user(user)
        await ctx.send(f"{user.mention}님에게 '{역할}' 역할이 부여되었습니다.")
    else:
        await ctx.send(f"{user.mention}님은 이미 '{역할}' 역할을 보유하고 있습니다.")

bot.run(os.getenv("TOKEN"))
