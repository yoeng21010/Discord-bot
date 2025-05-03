import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_NAMES = ["연맹원", "임원", "관리자"]
WELCOME_CHANNEL_NAME = "일반"

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

        removed_roles = []
        for role in user.roles:
            if role.name in ROLE_NAMES and role != new_role:
                await user.remove_roles(role)
                removed_roles.append(role.name)

        if new_role not in user.roles:
            await user.add_roles(new_role)
            msg = f"'{self.role_name}' 역할이 부여되었습니다!"
            if removed_roles:
                msg += f" (이전 역할: {', '.join(removed_roles)} 제거됨)"
        else:
            msg = f"'{self.role_name}' 역할은 이미 부여되어 있습니다."

        await interaction.response.send_message(msg, ephemeral=True)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        welcome_msg = f"""환영합니다 {member.mention}!!

간단한 서버에 관한 소개를 도와드릴게요!

1. 서버에 역할이 존재합니다! 들어오신 후 역할신청방에 본인의 역할(연맹원, 임원, 관리자) 중 하나를 선택해주세요! 역할 부여 후 서버 이용이 가능합니다.
2. 상호 간의 다툼 방지를 위해 공지-규칙 채널에서 규칙을 꼭 확인해 주세요!
3. 서버 확장, 제한 해제, 기타 서비스 요청은 서버 관리자나 임원에게 문의 부탁드립니다!

아래 버튼을 눌러 본인의 역할을 선택하세요!
"""
        await channel.send(welcome_msg, view=RoleSelectView())

@bot.command()
@commands.has_permissions(administrator=True)
async def 역할버튼(ctx):
    await ctx.send("역할을 선택하세요!", view=RoleSelectView())

@bot.command()
async def 권한(ctx):
    await ctx.send("아래 버튼을 눌러 본인의 역할을 선택하세요!", view=RoleSelectView())

bot.run(os.getenv("TOKEN"))
