from tabnanny import check
from unicodedata import category
from nextcord.ext import commands
import nextcord

import main
import time
from utils import guild_manager


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @commands.Cog.listener() 
    async def on_ready(self): #봇이 정상적으로 실행되었을 때 Activated! 를 IDE의 터미널에 출력합니다.
        print("Activated!")
        

    #메세지가 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.cached_message.author.bot: #봇의 메세지가 삭제되었을 때, 실행하지 않습니다. (즉, 유저 메세지의 로그만 표시됩니다.)
            return
        now = time.localtime() #삭제된 시간을 출력하기위함
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) #사용자가 선택한 로그채널의 ID를 가져옵니다. (채널의ID는 setting.txt에 저장되어 있습니다.)

        embed = nextcord.Embed(title="님의 메세지를 삭제하였습니다",    #삭제된 메세지의 정보를 출력하기 위해 임베드를 생성합니다.(디스코드의 임베드 기능)
                                description=f"Message deleted in <#{payload.cached_message.channel.id}>\n"
                                            f" Message deleted by {payload.name}", color=0x5947FF)
        embed.set_author(name=payload.cached_message.author, icon_url=payload.cached_message.author.display_avatar)
        embed.add_field(name="삭제된 메세지 내용", value=payload.cached_message.content, inline=False)
        embed.add_field(name="삭제된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        embed.add_field(name="IDs",
                        value=f"```diff\n+ {payload.cached_message.id}(message) \n+ "
                              f"{int(payload.guild_id)}(guild) \n"
                              f"+ {guild_manager.get_current_log_channel_id()}(channel)```",
                        inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed) #로그채널에 메세지를 전송합니다.

    #메세지가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: #봇의 메세지가 수정되었을 때, 실행하지 않습니다. (즉, 유저 메세지의 로그만 표시됩니다.)
            return
        elif after.author.bot: 
            return
        now = time.localtime()
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 

        embed = nextcord.Embed(title="님의 메세지를 수정하였습니다", #수정된 메세지의 정보를 출력하기 위해 임베드를 생성합니다.(디스코드의 임베드 기능)
                                description=f"메세지가 수정된 채널 <#{before.channel.id}>\n → [메세지 보기]({before.jump_url})", color=0xE189FC)
        embed.set_author(name=before.author, icon_url=before.author.display_avatar)
        embed.add_field(name="수정전 메세지 내용", value=before.content, inline=True)
        embed.add_field(name="수정후 메세지 내용", value=after.content, inline=True)
        embed.add_field(name="수정된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        embed.add_field(name="IDs",
                        value = f"```diff\n+ {before.id} (message) \n+ "
                                f"{int(before.guild.id)} (guild) \n+ "
                                f"{before.channel.id} (channel) ```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")

        await channel.send(embed=embed) #로그채널에 메세지를 전송합니다.
    
    #서버 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        now = time.localtime()
        checking = False
        embed = nextcord.Embed(title="서버 정보가 수정되었습니다", color=0xFFF700)
        embed.set_author(name=after.name, icon_url=after.icon)
        if before.name != after.name:
            embed.add_field(name="name", value=f"{before.name} → {after.name}", inline=False)
            checking = True
        if before.afk_channel != after.afk_channel:
            embed.add_field(name="afk_channel", value=f"{before.afk_channel} → {after.afk_channel}", inline=True)
            checking = True
        if before.afk_timeout != after.afk_timeout:
            embed.add_field(name="afk_timeout", value=f"{before.afk_timeout} → {after.afk_timeout}\n(second)", inline=True)
            checking = True
        if checking == True:
            embed.add_field(name="owner", value=f"{before.owner.name}", inline=False)
            embed.add_field(name="수정된 시일", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
                            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
            embed.add_field(name="Guild id",
                            value = f"```diff\n+ {int(after.id)} (guild)```", inline=False)
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)                       

    #유저, 봇이 서버에 입장했을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 

        embed = nextcord.Embed(title=f"님이 서버에 입장하셨습니다", color=0x00FF00)
        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.add_field(name="서버에 입장한 시일",
                        value=f"``{guild_manager.utc_to_kst(member.joined_at)}``", #utc_to_kst는 서버에 입장한 시간을 UTC표준시간에서 한국시간으로 변환해주는 함수입니다.
                        inline=True)
        embed.add_field(name="USER ID", value=f"```diff\n+ {member.id}```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")

        await channel.send(embed=embed)

    #유저, 봇이 서버에서 나갔을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        now = time.localtime()

        embed = nextcord.Embed(title="님이 서버에서 나가셨습니다", color=0xFF0000)
        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.add_field(name="서버에서 나간 시일",
                        value=f"``%04d-%02d-%02d %02d:%02d:%02d``" % (
                        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        embed.add_field(name="USER ID", value=f"```diff\n+ {member.id}```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")

        await channel.send(embed=embed)


    #서버에서 초대코드가 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        embed = nextcord.Embed(title=f"<#{invite.channel.name}> 채널에서 초대코드가 생성되었습니다", color=0x86FFC3)
        embed.add_field(name="생성자",value=f"``{invite.inviter}``", inline=True)
        embed.add_field(name="초대코드",value=f"{invite.code}", inline=True)
        embed.add_field(name="초대코드 만료기간",value=f"``{invite.expires_at}``\n(UTC+00:00 기준)", inline=True)
        if invite.max_uses == 0:
            embed.add_field(name="초대인원 제한",value=f"``무제한``", inline=True)
        else:
            embed.add_field(name="초대인원 제한",value=f"``{invite.max_uses}명``", inline=True)
        embed.add_field(name="임시초대여부",value=f"{invite.temporary}", inline=True)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed)

    #서버에서 초대코드가 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        now = time.localtime()
        embed = nextcord.Embed(title=f"<#{invite.channel.name}> 채널에서 초대코드가 삭제되었습니다", color=0xFF0000)
        embed.add_field(name="초대코드",value=f"{invite.code}", inline=True)
        embed.add_field(name="초대코드가 삭제된 일시",value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
                        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=True)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed)

     #새로운 채널이 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        if str(channel.type) == 'text':
            embed = nextcord.Embed(title="텍스트 채널이 생성되었습니다")
        elif str(channel.type) == 'voice':
            embed = nextcord.Embed(title="보이스 채널이 생성되었습니다")
        elif str(channel.type) == 'category':
            embed = nextcord.Embed(title="카테고리 채널이 생성되었습니다")
        embed.add_field(name="name", value=f"{channel}", inline=True)
        embed.add_field(name="채널이 생성된 시일", value=f"{guild_manager.utc_to_kst(channel.created_at)}", inline=False)
        embed.add_field(name="Category", value=f"{channel.category}", inline=False)
        embed.add_field(name="position", value=f"{channel.position}", inline=False)
        embed.add_field(name="IDs", value=f"```diff\n+ {channel.id} (channel) \n+ "
                        f"{int(channel.guild.id)} (guild)```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await log_channel.send(channel.last_message)

    #채널이 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        now = time.localtime()
        if str(channel.type) == 'text':
            embed = nextcord.Embed(title="텍스트 채널이 삭제되었습니다", color=0x37393E)
        elif str(channel.type) == 'voice':
            embed = nextcord.Embed(title="보이스 채널이 삭제되었습니다", color=0x37393E)
        elif str(channel.type) == 'category':
            embed = nextcord.Embed(title="카테고리 채널이 삭제되었습니다", color=0x37393E)
        embed.add_field(name="name", value=f"{channel}", inline=True)
        embed.add_field(name="삭제된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        embed.add_field(name="IDs", value=f"```diff\n+ {channel.id} (channel) \n+ "
                        f"{int(channel.guild.id)} (guild)```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await log_channel.send(embed=embed)

    #채널이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        checking = False
        if str(channel.type) == 'category':
            embed = nextcord.Embed(title=f"{before.name} 카테고리가 업데이트 되었습니다", color=0xFFF700)
        else:
           embed = nextcord.Embed(title=f"{before.name} 채널이 업데이트 되었습니다", color=0xFFF700)
        
        if(before.name != after.name):
            embed.add_field(name="이름",value=f"{before.name} → {after.name}", inline=False)
            checking = True
        if(before.category != after.category):
            embed.add_field(name="카테고리",value=f"{before.category} → {after.category}", inline=False)
            checking = True
        if(before.topic != after.topic):
            embed.add_field(name="변경전 채널주제",value=f"{before.topic}", inline=True)
            embed.add_field(name="변경후 채널주제",value=f"{after.topic}", inline=True)
            checking = True
        if (before.nsfw != after.nsfw):
            if(before.nsfw == True):
                embed.add_field(name="NSFW",value=f"YES → NO", inline=False)
            else:
                embed.add_field(name="NSFW",value=f"NO → YES", inline=False)
            checking = True
        if(checking == True):
                embed.set_footer(text="Developed by 동건#3038")
                await channel.send(embed=embed)
        #채널의 권한이 추가되면, 선택된 로그채널로 로그메세지를 전송합니다. (미완성)
        '''
        if(before.changed_roles != after.changed_roles):
            if(before.changed_roles == None):
                embed.add_field(name="추가된 역할",value={before.changed_roles[1]}, inline=False)
            else:
                embed.add_field(name="삭제된 역할",value=f"{before.changed_roles[1]}", inline=False)
            checking = True
        '''

    #음성상태 , 보이스채널이 변경되면, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False
        if before.channel != after.channel:    
            if before.channel == None and after.channel != None:
                embed = nextcord.Embed(title=f"{member.name}님이 보이스 채널에 입장하였습니다.", color=0x37393E)
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name="Channel",value=f"[{after.channel.name}]({after.channel.jump_url})", inline=True)
                checking = True
            elif before.channel != None and after.channel == None:
                embed = nextcord.Embed(title=f"{member.name}님이 보이스 채널에서 나가셨습니다.", color=0x37393E)
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name="Channel",value=f"[{before.channel.name}]({before.channel.jump_url})", inline=True)
                checking = True
            elif before.channel != after.channel:
                embed = nextcord.Embed(title=f"{member.name}님이 보이스 채널을 이동하셨습니다.", color=0x37393E)
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name="Before Channel",value=f"[{before.channel.name}]({before.channel.jump_url}) ", inline=True)
                embed.add_field(name="After Channel",value=f"[{after.channel.name}]({after.channel.jump_url}) ", inline=True)
                checking = True
            else:
                embed = nextcord.Embed(title=f"에러가 발생하였습니다!", color=0xFFFFFF)
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name="에러구분",value=f"on_voice_state_update", inline=True)
                checking = True
            
            
            checking = True
        if before.deaf != after.deaf:
            embed = nextcord.Embed(title=f"{member.name}님의 음성 상태가 변경되었습니다.", color=0x37393E)
            embed.set_author(name=member, icon_url=member.display_avatar)
            embed.add_field(name="deaf changes",value=f"{before.deaf} → {after.deaf}", inline=True)
            embed.add_field(name="mute changes",value=f"{before.mute} → {after.mute}", inline=True)
            embed.add_field(name="afk",value=f"{before.afk} → {after.afk}", inline=True)
            checking = True
        if checking == True:
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)



    #비공개 채널이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_private_channel_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id()) 
        checking = False

        if str(channel.type) == 'category':
            embed = nextcord.Embed(title=f"{before.name} 카테고리가 업데이트 되었습니다", color=0xFFF700)
        else:
           embed = nextcord.Embed(title=f"{before.name} 채널이 업데이트 되었습니다", color=0xFFF700)

        if(before.name != after.name):
            embed.add_field(name="이름",value=f"{before.name} → {after.name}", inline=False)
            checking = True
        if(before.category != after.category):
            embed.add_field(name="카테고리",value=f"{before.category} → {after.category}", inline=False)
            checking = True
        if(before.topic != after.topic):
            embed.add_field(name="변경전 채널주제",value=f"{before.topic}", inline=True)
            embed.add_field(name="변경후 채널주제",value=f"{after.topic}", inline=True)
            checking = True
        if (before.nsfw != after.nsfw):
            if(before.nsfw == True):
                embed.add_field(name="NSFW",value=f"YES → NO", inline=False)
            else:
                embed.add_field(name="NSFW",value=f"NO → YES", inline=False)
            checking = True
        if(checking == True):
                embed.set_footer(text="Developed by 동건#3038")
                await channel.send(embed=embed)
   

        #역할이 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed=nextcord.Embed(title=f"<{role.name}> 역할이 생성되었습니다", color=0x00FF22)
        embed.add_field(name="IDs", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed)


        #역할이 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed=nextcord.Embed(title=f"<{role.name}> 역할이 삭제되었습니다", color=0xFF0000)
        embed.add_field(name="IDs", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed)

        #역할이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False
        embed=nextcord.Embed(title=f"<{before.name}> 역할이 업데이트 되었습니다", color=after.colour)
        if(before.name != after.name):
            embed.add_field(name=f"{before.name} -> {after.name}", inline=False)
            checking = True
        if(before.colour != after.colour):
            embed.add_field(name="색상", value=f"{before.colour} -> {after.colour}(임베드색상)", inline=False)
            checking = True
        #기능은 잘 작동하나,,, 역할 한개가 바뀌면 position이 모두 변경되는 바람에 쓸대없이 로그메세지를 많이 전송하여... → 주석처리 해둠
        '''
        if(before.position != after.position):
            embed.add_field(name="순서(position)", value=f"{before.position} -> {after.position}", inline=False)
            checking = True
        '''
        if(before.hoist != after.hoist):
            embed.add_field(name="역할 분리여부(Hoist)", value=f"{before.hoist} -> {after.hoist}", inline=False)
            checking = True
        if(before.mentionable != after.mentionable):
            embed.add_field(name="멘션", value=f"{before.mentionable} -> {after.mentionable}", inline=False)
            checking = True
        if(checking == True):
            embed.add_field(name="IDs", value=f"```diff\n+ {after.id} (role) \n+ {int(after.guild.id)} (guild)```", inline=False)
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)

        #유저의 서버 프로필 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed=nextcord.Embed(title=f"{after.name}님의 서버 정보가 수정되었습니다", color=0x00FF00)
        checkig = False
        if(before.display_name != after.display_name):
            embed.add_field(name="Nickname", value=f"{before.display_name} -> {after.display_name}", inline=False)
            checking = True
        if checking == True:
            embed.add_field(name="Guild ID", value=f"```diff\n+ {int(after.guild.id)}```", inline=False)
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)

        #유저의 개인 프로필 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed=nextcord.Embed(title=f"{after.name}님의 프로필 정보가 수정되었습니다", color=0x00FF00)
        checking = False
        if before.name != after.name:
            embed.add_field(name="Profile name", value=f"{before.name} -> {after.name}", inline=False)
            checking = True
        if before.discriminator != after.discriminator:
            embed.add_field(name="discriminator", value=f"{before.discriminator} -> {after.discriminator}", inline=False)
            checking = True
        if before.avatar != after.avatar:
            embed.add_field(name="Profile avatar", value=f"{before.display_avatar} ```->``` {after.display_avatar}", inline=False)
            checking = True
        if checking == True:
            embed.add_field(name="User ID", value=f"```diff\n+ {int(after.id)} (user)```", inline=False)
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)



def setup(bot):
    bot.add_cog(Event(bot))