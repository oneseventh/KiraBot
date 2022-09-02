"""
    #제작: @donggeon  #수정: @17th
    #최종 수정일: 2022년 09월 01일
"""

from nextcord.ext import commands
import nextcord
import datetime
import main
import time
from utils import guild_manager, kira_language


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    # 메세지가 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.cached_message.author.bot:  # 봇의 메세지가 삭제되었을 때, 실행하지 않습니다. (즉, 유저 메세지의 로그만 표시됩니다.)
            return
        if not guild_manager.is_guild_registered(payload.guild_id):
            return
        now = time.localtime()  # 삭제된 시간을 출력하기위함
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id(payload.guild_id))  # 사용자가 선택한 로그채널의 ID를 가져옵니다.
        # (채널의ID는 setting.txt에 저장되어 있습니다)
        Embed = nextcord.Embed(title=kira_language.get_text("log-message-deleted-embed-title"),
                               # 삭제된 메세지의 정보를 출력하기 위해 임베드를 생성합니다.(디스코드의 임베드 기능)
                               description=kira_language.get_text("log-message-deleted-embed-description")
                               .format(payload.cached_message.channel.id), color=0x5337EF)
        # alert.embed.title.message.delete: Message has been deleted
        # alert.embed.description.message.delete: Message deleted in <#{0}>
        Embed.set_author(name=payload.cached_message.author, icon_url=payload.cached_message.author.display_avatar)
        Embed.add_field(name=kira_language.get_text("log-message-deleted-embed-field-message-content"),
                        value=payload.cached_message.content, inline=False)
        # alert.embed.field.title.delete.message.content: Deleted Message Content
        Embed.add_field(name=kira_language.get_text("log-message-deleted-embed-field-deleted-date"),
                        value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
                            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        # alert.embed.field.title.deleted.date: Deleted date
        Embed.add_field(name="ID",
                        value=f"```diff\n+ {payload.cached_message.id} (Message ID) \n"
                              f"+ {payload.channel_id} (Channel ID)```",
                        inline=False)
        # alert.embed.field.title.id: ID
        Embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=Embed)  # 로그채널에 메세지를 전송합니다.

    # 메세지가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:  # 봇의 메세지가 수정되었을 때, 실행하지 않습니다. (즉, 유저 메세지의 로그만 표시됩니다.)
            return
        elif after.author.bot:
            return

        now = time.localtime()
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id(self.bot.guild.id))

        Embed = nextcord.Embed(title=kira_language.get_text("log-message-edited-embed-title"),
                               # 수정된 메세지의 정보를 출력하기 위해 임베드를 생성합니다.(디스코드의 임베드 기능)
                               description=kira_language.get_text("log-message-edited-embed-description")
                               .format(before.channel.id) +
                                           f"[{kira_language.get_text('log-message-edited-embed-field-jump-to')}]"
                                           f"({before.jump_url})", color=0xFEFF9F)
        # alert.embed.title.message.edited: Message has been edited
        # alert.embed.description.message.edited: The message edited in <#{0}>\n → [Jump to Message]({1})
        Embed.set_author(name=before.author, icon_url=before.author.display_avatar)
        Embed.add_field(name=kira_language.get_text("log-message-edited-embed-field-previous-message-content"),
                        value=before.content, inline=True)
        # alert.embed.field.message.edited.content.past: Previous message content
        Embed.add_field(name=kira_language.get_text("log-message-edited-embed-field-current-message-content"),
                        value=after.content, inline=True)
        # alert.embed.field.message.edited.content.now: Current message content
        Embed.add_field(name=kira_language.get_text("log-message-edited-embed-field-edited-date"),
                        value="``%04d-%02d-%02d %02d:%02d:%02d`` (KST)" % (
                            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        # alert.embed.field.message.edited.date: Edited date
        Embed.add_field(name="ID",
                        value=f"```diff\n+ {before.id} (Message ID) \n+ "
                              f"{before.channel.id} (Channel ID) ```", inline=False)
        # alert.embed.field.title.id: ID
        Embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=Embed)  # 로그채널에 메세지를 전송합니다.

    # 서버 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        now = time.localtime()
        log_checking = False

        '''
        if int(before.member_count) >= int(after.member_count):  # 서버의 인원수가 줄어들었을 때, 밴 당한 사람이 없는지 확인하고 출력
            async for entry in before.audit_logs(action=nextcord.AuditLogAction.ban):
                if entry != "" or entry is not None:
                    ban_embed = nextcord.Embed(title=f"Someone has been banned", color=0xFF000F)
                    ban_embed.add_field(name="Banned", value=f"<@{entry.target.id}>got banned by<@{entry.user.id}>",
                                    inline=False)
                    ban_embed.set_footer(text="Developed by 동건#3038")
                    await channel.send(embed=ban_embed)
                else:
                    break

        unbaner = ""
        async for entry in before.audit_logs(action=nextcord.AuditLogAction.unban):
            if entry is not "" or entry is not None or entry is not False:
                Embed.add_field(name="Unbanned", value=f"<@{entry.target.id}>got unbanned by<@{entry.user.id}>",
                                inline=False)
        '''

        editor = ""
        async for entry in before.audit_logs(action=nextcord.AuditLogAction.guild_update, limit=1):
            logtime = guild_manager.int_utc_to_kst(entry.created_at)
            logtime = int(time.mktime(logtime.timetuple()))
            runtime = datetime.datetime.now()
            runtime = int(time.mktime(runtime.timetuple()))
            if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                editor = entry.user.id
            else:
                editor = ""
        if editor == "":
            log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-updated-embed-title"),
                                       description=kira_language.get_text("log-guild-updated-embed-unknown"
                                                                          "-description"),
                                       color=0xFFA700)
            # alert.embed.title.server.updated: Server updated
            # alert.embed.description.Unknown: Server updated by Unknownd
        else:
            log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-updated-embed-title"),
                                       description=kira_language.get_text("log-guild-updated-embed-description").format(
                                           editor), color=0xFFA700)
            # alert.embed.title.server.updated: Server updated
            # alert.embed.description.editor: Server updated by <@{0}>
        log_embed.set_author(name=after.name, icon_url=after.icon)
        if before.name != after.name:
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-server-name"),
                                value=f"``{before.name}`` → ``{after.name}``", inline=False)
            # alert.embed.field.title.name: Name
            log_checking = True
        if before.afk_channel != after.afk_channel:
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-afk-channel"),
                                value=f"<#{before.afk_channel.id}> → <#{after.afk_channel.id}>",
                                inline=True)  # alert.embed.field.title.afk.channel: AFK Channel
            log_checking = True
        if before.afk_timeout != after.afk_timeout:
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-afk-timeout"),
                                value=f"``{before.afk_timeout}s`` → ``{after.afk_timeout}s``",
                                inline=True)  # alert.embed.field.title.afk.timeout: AFK Timeout
            log_checking = True
        # if before.region != after.region:
        #     log_embed.add_field(name="Region Changes", value=f"{before.region} → {after.region}", inline=True)
        #     # alert.embed.field.title.region: Region Changes
        #     log_checking = True
        # if before.banner != after.banner:
        #     log_embed.add_field(name="Banner Changes", value=f"{before.banner} → {after.banner}", inline=True)
        #     # alert.embed.field.title.banner: Banner Changes
        #     log_checking = True
        if before.verification_level != after.verification_level:
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-verification-level"),
                                value=f"``{before.verification_level}`` → ``{after.verification_level}``",
                                inline=True)
            # alert.embed.field.title.Verification.Level: Verification Level
            log_checking = True
            # if before.discovery_splash != after.discovery_splash:
            #    log_embed.add_field(name="Discovery Splash", value=f"{before.discovery_splash} → {after.discovery_splash}",
            #                         inline=True)  # alert.embed.field.title.Discovery.Splash: Discovery Splash
            log_checking = True
        if log_checking:
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-owner"),
                                value=f"<@{before.owner.id}>", inline=False)
            # alert.embed.field.title.Owner: Owner
            log_embed.add_field(name=kira_language.get_text("log-guild-updated-embed-field-date"),
                                value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
                                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec),
                                inline=False)
            # alert.embed.field.changed.date: Changed Date
            log_embed.add_field(name="Guild ID",  # alert.embed.field.title.Guild.id: Guild id
                                value=f"```diff\n+ {int(after.id)} (Guild ID)```", inline=False)
            log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=log_embed)

            # 유저, 봇이 서버에 입장했을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())

        log_embed = nextcord.Embed(title=kira_language.get_text("log-join-embed-title"), color=0x7FFF91)
        # alert.embed.title.server.connect: Member Joined
        log_embed.set_author(name=member, icon_url=member.display_avatar)
        log_embed.add_field(name=kira_language.get_text("log-join-embed-date"),
                            value=f"``{guild_manager.utc_to_kst(member.joined_at)}`` (KST)",
                            # utc_to_kst는 서버에 입장한 시간을 UTC표준시간에서 한국시간으로 변환해주는 함수입니다.
                            inline=True)
        # alert.embed.field.title.join.date: join date
        log_embed.add_field(name="User ID", value=f"```diff\n+ {member.id}```", inline=False)
        # alert.embed.field.title.user.id: User ID
        log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=log_embed)

    # 유저, 봇이 서버에서 나갔을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        now = time.localtime()

        log_embed = nextcord.Embed(title=kira_language.get_text("log-left-embed-date"), color=0xFF5544)
        # alert.embed.field.title.server.disconnect: Memeber Leaved
        log_embed.set_author(name=member, icon_url=member.display_avatar)
        log_embed.add_field(name=kira_language.get_text("log-left-embed-date"),
                            value=f"``%04d-%02d-%02d %02d:%02d:%02d``" % (
                                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec),
                            inline=False)
        # alert.embed.field.title.leave.date: Leave Date
        log_embed.add_field(name="User ID", value=f"```diff\n+ {member.id}```", inline=False)
        # alert.embed.field.title.user.id: User ID
        log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=log_embed)

    # 서버에서 초대코드가 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        Embed = nextcord.Embed(title=kira_language.get_text("log-invite-embed-title"),
                               description=kira_language.get_text("log-invite-embed-description")
                               .format(invite.channel.id), color=0xC1FFDF)
        # alert.embed.field.title.invite.code.created: Invite code created in <#{0}>
        Embed.add_field(name=kira_language.get_text("log-invite-embed-field-inviter"),
                        value=f"``{invite.inviter}``", inline=True)
        # alert.embed.field.title.inviter: made by
        Embed.add_field(name=kira_language.get_text("log-invite-embed-field-invite-code"),
                        value=f"``{invite.code}``", inline=True)
        # alert.embed.field.title.invite.code: Invite code
        Embed.add_field(name=kira_language.get_text("log-invite-embed-field-invite-expire"),
                        value=f"``{guild_manager.utc_to_kst(invite.expires_at)}``",
                        inline=True)
        # alert.embed.field.title.invite.code.expires.at: Invite code Expires at
        if invite.max_uses == 0:
            Embed.add_field(name=kira_language.get_text("log-invite-embed-field-invite-maxium"),
                            value=kira_language.get_text("log-invite-embed-field-invite-maxium-unlimited"), inline=True)
            # alert.embed.field.title.use.limit.invite.code: Maximum invite limit
            # alert.embed.field.value.unlimited: unlimited
        else:
            Embed.add_field(name=kira_language.get_text("log-invite-embed-field-invite-maxium"),
                            value=f"``{invite.max_uses}``", inline=True)
            # alert.embed.field.title.use.limit.invite.code: Maximum invite limit
        Embed.add_field(name=kira_language.get_text("log-invite-embed-field-is-temporary"),
                        value=f"``{invite.temporary}``", inline=True)
        # alert.embed.field.title.invite.temporary: Temporary of invite code
        Embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=Embed)

    # 서버에서 초대코드가 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        now = time.localtime()
        log_embed = nextcord.Embed(title=kira_language.get_text("log-invite-delete-embed-title"),
                                   description=kira_language.get_text("log-invite-delete-embed-description")
                                   .format(invite.channel.id),
                                   color=0xFF5544)
        # alert.embed.field.title.invite.code.deleted: Invite code deleted in <#{0}>
        log_embed.add_field(name=kira_language.get_text("log-invite-delete-embed-field-invite-code"),
                            value=f"``{invite.code}``", inline=True)
        # alert.embed.field.title.invite.code: Invite code
        log_embed.add_field(name=kira_language.get_text("log-invite-delete-embed-field-invite-date"),
                            value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
                                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=True)
        # alert.embed.field.title.invite.code.expires.at: Invite code Expires at
        log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=log_embed)

    # 새로운 채널이 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        global log_embed
        log_channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        if str(channel.type) == 'text':
            creater = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_create, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    creater = entry.user.id
                else:
                    creater = ""
            if creater == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-chat-created-embed-title"),
                                           description=
                                       kira_language.get_text("log-guild-channel-created-embed-unknown-description"),
                                           color=0xFFA700)
                # alert.embed.title.channel.created: Channel created
                # alert.embed.description.channel.created.by.unknown: Channel created by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-chat-created-embed-title"),
                                           description=
                                       kira_language.get_text("log-guild-channel-created-embed-description")
                                           .format(creater), color=0xFFA700)
                # alert.embed.title.channel.created: Channel created
                # alert.embed.description.channel.created.by: Channel created by <@{0}>
            log_embed.add_field(name=kira_language.get_text("log-guild-channel-created-embed-field-channel"),
                                value=f"<#{channel.id}>", inline=True)
        elif str(channel.type) == 'voice':
            creater = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_create, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    creater = entry.user.id
                else:
                    creater = ""
            if creater == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-voice-created-embed-title"),
                                           description=
                                       kira_language.get_text("log-guild-channel-created-embed-unknown-description"), color=0xFFA700)
                # alert.embed.title.channel.created: Channel Created
                # alert.embed.description.channel.created.by.unknown: Channel created by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-voice-created-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-created-embed-description")
                                           .format(creater), color=0xFFA700)
                # alert.embed.title.channel.created: Channel Created
                # alert.embed.description.channel.created.by: Channel created by <@{0}>
            log_embed.add_field(name=kira_language.get_text("log-guild-channel-created-embed-field-channel"),
                                value=f"<#{channel.id}>", inline=True)
        elif str(channel.type) == 'category':
            creater = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_create, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    creater = entry.user.id
                else:
                    creater = ""
            if creater == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-category-created-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-created-embed-unknown-description"),
                                           color=0xFFA700)
                # alert.embed.title.Category.created: Category Created
                # alert.embed.description.Category.created.by.unknown: Category created by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-category-created-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-created-embed-description")
                                           .format(creater), color=0xFFA700)
                # alert.embed.title.category.created: Category Created
                # alert.embed.description.category.created.by: Category created by <@{0}>
            log_embed.add_field(name=kira_language.get_text("log-guild-channel-created-embed-field-category-name"),
                                value=f"``{channel}``", inline=True)
        # alert.embed.field.title.name: Name
        log_embed.add_field(name=kira_language.get_text("log-guild-channel-created-embed-field-channel-created"),
                            value=f"``{guild_manager.utc_to_kst(channel.created_at)}``",
                            inline=False)
        # alert.embed.field.channel.created.date: Created Date
        log_embed.add_field(name="ID", value=f"```diff\n+ {channel.id} (Channel ID) \n+ "
                                         f"{int(channel.guild.id)} (Guild ID)```", inline=False)
        # alert.embed.field.title.id: ID
        log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await log_channel.send(embed=log_embed)

    # 채널이 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        global log_embed
        log_channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        now = time.localtime()
        if str(channel.type) == 'text':
            deleter = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_delete, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    deleter = entry.user.id
                else:
                    deleter = ""
            if deleter == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-chat-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-unknown"
                                                                          "-description")
                                           , color=0xFFA700)
                # alert.embed.title.channel.deleted: Channel Deleted
                # alert.embed.description.channel.deleted.by.unknown: Channel deleted by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-chat-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-description")
                                           .format(deleter), color=0xFFA700)
                # alert.embed.title.channel.deleted: Channel Deleted
                # alert.embed.description.channel.deleted.by: Channel deleted by <@{0}>
        elif str(channel.type) == 'voice':
            deleter = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_delete, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    deleter = entry.user.id
                else:
                    deleter = ""
            if deleter == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-voice-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-unknown"
                                                                          "-description")
                                           , color=0xFFA700)
                # alert.embed.title.channel.deleted: Channel Deleted
                # alert.embed.description.channel.deleted.by.unknown: Channel deleted by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-voice-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-description")
                                           .format(deleter), color=0xFFA700)
                # alert.embed.title.channel.deleted: Channel Deleted
                # alert.embed.description.channel.deleted.by: Channel deleted by <@{0}>
        elif str(channel.type) == 'category':
            deleter = ""
            async for entry in channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_delete, limit=1):
                logtime = guild_manager.int_utc_to_kst(entry.created_at)
                logtime = int(time.mktime(logtime.timetuple()))
                runtime = datetime.datetime.now()
                runtime = int(time.mktime(runtime.timetuple()))
                if (runtime - logtime) <= 2:  # 현재 시간과 마지막 member_move 감사로그의 시간을 비교함
                    deleter = entry.user.id
                else:
                    deleter = ""
            if deleter == "":
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-category-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-unknown"
                                                                          "-description")
                                           , color=0xFFA700)
                # alert.embed.title.category.deleted: Category Deleted
                # alert.embed.description.category.deleted.by.unknown: Category deleted by Unknown
            else:
                log_embed = nextcord.Embed(title=kira_language.get_text("log-guild-channel-category-deleted-embed-title"),
                                           description=kira_language.get_text("log-guild-channel-deleted-embed-description")
                                           .format(deleter), color=0xFFA700)
                # alert.embed.title.category.deleted: Category Deleted
                # alert.embed.description.category.deleted.by: Category deleted by <@{0}>
        log_embed.add_field(name=kira_language.get_text("log-guild-channel-deleted-embed-field-name"),
                            value=f"``{channel}``", inline=False)
        # alert.embed.field.title.name: Name
        log_embed.add_field(name=kira_language.get_text("log-guild-channel-deleted-embed-field-channel-created"),
                            value=f"``{guild_manager.utc_to_kst(channel.created_at)}``",
                            inline=True)
        # alert.embed.field.title.channel.created.date: Created date
        log_embed.add_field(name=kira_language.get_text("log-guild-channel-deleted-embed-field-channel-deleted"),
                            value="``%04d-%02d-%02d %02d:%02d:%02d``" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
        # alert.embed.field.title.deleted.date: Deleted Date
        log_embed.add_field(name="ID", value=f"```diff\n+ {channel.id} (Chennel ID) \n+ "
                                         f"{int(channel.guild.id)} (Guild ID)```", inline=False)
        # alert.embed.field.title.id: ID
        log_embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
        # alert.embed.footer.title: Developed by 동건#3038
        await log_channel.send(embed=log_embed)

    # 채널이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False
        global embed
        if str(channel.type) == 'category':
            embed = nextcord.Embed(title=f"Category updated [{before.name}]", color=0xFFA700)
            # alert.embed.title.guild.channel.category.updated: 카테고리가 업데이트 되었습니다 [{0}]
        else:
            embed = nextcord.Embed(title=f"Channel updated [{before.name}]", color=0xFFA700)
            # alert.embed.title.guild.channel.updated: Channel updated [{0}]
        if before.name is not after.name:
            embed.add_field(name="Name", value=f"{before.name} → {after.name}", inline=False)
            # alert.embed.field.title.guild.channel.name.updated: Name
            checking = True
        if before.category is not after.category:
            embed.add_field(name="Category", value=f"{before.category} → {after.category}", inline=False)
            # alert.embed.field.title.guild.channel.category.updated: Category
            checking = True
        if before.topic is not after.topic:
            embed.add_field(name="Previous channel topic", value=f"{before.topic}", inline=True)
            # alert.embed.field.title.guild.channel.before.topic.updated: Previous channel topic
            embed.add_field(name="Current channel topic", value=f"{after.topic}", inline=True)
            # alert.embed.field.title.guild.channel.after.topic.updated: Current channel topic
            checking = True
        if before.nsfw is not after.nsfw:
            if before.nsfw is True:
                embed.add_field(name="NSFW", value=f"YES → NO", inline=False)
                # alert.embed.field.title.guild.channel.nsfw.updated: NSFW
            else:
                embed.add_field(name="NSFW", value=f"NO → YES", inline=False)
                # alert.embed.field.title.guild.channel.nsfw.updated: NSFW
            checking = True
        if checking:
            embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)
        # 채널의 권한이 추가되면, 선택된 로그채널로 로그메세지를 전송합니다. (미완성)
        '''
        if(before.changed_roles != after.changed_roles):
            if(before.changed_roles == None):
                Embed.add_field(name="추가된 역할",value={before.changed_roles[1]}, inline=False)
            else:
                Embed.add_field(name="삭제된 역할",value=f"{before.changed_roles[1]}", inline=False)
            checking = True
        '''

    # 음성상태 , 보이스채널이 변경되면, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global embed
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False

        if before.channel != after.channel:
            if before.channel is None and after.channel is not None:
                embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-join-title"), color=0x37393E)
                # alert.embed.title.guild.voice.state.channel.joined: Joined voice channel
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name="Channel", value=f"[<#{after.channel.id}>]({after.channel.jump_url})", inline=True)
                # alert.embed.field.title.guild.voice.state.joined.channel: Channel
            elif before.channel is not None and after.channel is None:
                deleter = ""
                deleter = await guild_manager.get_audit_log(member.guild, nextcord.AuditLogAction.member_disconnect,
                                                            member.id)
                if member.id == deleter:
                    embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-quit-title"),
                                           color=0x37393E)
                    # alert.embed.title.guild.voice.state.channel.leave: Laved voice channel
                else:
                    if deleter is None:
                        return
                    embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-kicked-title"),
                                           description=kira_language.get_text("log-guild-voide-embed-field-kicked-by")
                                           .format(deleter), color=0x37393E)
                    # alert.embed.title.guild.voice.state.channel.kicked: Kicked from voice channel
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-channel"),
                                value=f"[<#{before.channel.id}>]({before.channel.jump_url})",
                                inline=True)
                # alert.embed.field.title.guild.voice.state.from.channel.leave: Channel
            elif before.channel is not after.channel:
                deleter = ""
                deleter = await guild_manager.get_audit_log(member.guild, nextcord.AuditLogAction.member_move,
                                                            member.id)
                if member.id == deleter:
                    embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-moved-title"), color=0x37393E)
                    # alter.embed.field.title.voice.state.updated.moved.voice.channel: Moved voice channel
                else:
                    if deleter is None:
                        return
                    embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-moved-title"),
                                           description=kira_language.get_text("log-guild-voice-embed-field-moved-by")
                                           .format(deleter), color=0x37393E)
                    # alter.embed.field.title.voice.state.updated.moved.voice.channel: Moved voice channel
                embed.set_author(name=member, icon_url=member.display_avatar)
                embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-before"),
                                value=f"[<#{before.channel.id}>]({before.channel.jump_url}) ",
                                inline=True)
                # alter.embed.field.title.voice.state.updated.move.channel.before: Before Channel
                embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-after"),
                                value=f"[<#{after.channel.id}>]({after.channel.jump_url}) ",
                                inline=True)
                # alter.embed.field.title.voice.state.updated.move.channel.after: After Channel
            checking = True
        if before.deaf is not after.deaf or before.mute is not after.mute or before.afk is not after.afk:
            changer = ""
            changer = await guild_manager.get_audit_log(member.guild, nextcord.AuditLogAction.member_update, member.id)
            if member.id == changer:
                embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-force-title"),
                                       description=kira_language.get_text("log-guild-voice-embed-force-"
                                                                          "unknown-description")
                                       .format(member.id), color=0x37393E)
                # alert.embed.title.voice.status.updated.by: Voice status updated <@{0}>
                # alert.embed.description.voice.status.updated.by.unknown: Updated by Unknown
            else:
                embed = nextcord.Embed(title=kira_language.get_text("log-guild-voice-embed-force-title"),
                                       description=kira_language.get_text("log-guild-voice-embed-force-"
                                                                          "description")
                                       .format(changer, member.id), color=0x37393E)
            # alert.embed.title.voice.status.updated.by: Voice status updated <@{0}>
            # alert.embed.description.voice.status.updated.by: Updated by <@{0}>
            embed.set_author(name=member, icon_url=member.display_avatar)
            if before.deaf is not after.deaf:
                if before.deaf is True:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-deaf"),
                                    value=f"``YES`` → ``NO``", inline=False)
                    # alert.embed.field.title.voice.status.updated.deaf: Deaf
                else:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-deaf"),
                                    value=f"``NO`` → ``YES``", inline=False)
                    # alert.embed.field.title.voice.status.updated.deaf: Deaf
            if before.mute is not after.mute:
                if before.mute is True:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-mute"),
                                    value=f"``YES`` → ``NO``", inline=False)
                    # alert.embed.field.title.voice.status.updated.mute: Mute
                else:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-mute"),
                                    value=f"``NO`` → ``YES``", inline=False)
                    # alert.embed.field.title.voice.status.updated.mute: Mute
            if before.afk is not after.afk:
                if before.afk is True:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-afk"),
                                    value=f"``YES`` → ``NO``", inline=False)
                    # alert.embed.field.title.voice.status.updated.afk: AFK
                else:
                    embed.add_field(name=kira_language.get_text("log-guild-voice-embed-field-afk"),
                                    value=f"``NO`` → ``YES``", inline=False)
                    # alert.embed.field.title.voice.status.updated.afk: AFK
            checking = True
        if checking:
            embed.set_footer(text="Developed by {0}".format(kira_language.get_text("PART2_DEVELOPER_NAME")))
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)

    # 비공개 채널이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.
    @commands.Cog.listener()
    async def on_private_channel_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False

        if str(channel.type) == 'category':
            embed = nextcord.Embed(title=f"Category updated [{before.name}]", color=0xFFF700)
            # alert.embed.title.private.channel.category.updated: Category updated [{0}]
        else:
            embed = nextcord.Embed(title=f"Channel updated [{before.name}]", color=0xFFF700)
            # alert.embed.title.private.channel.channel.updated: Channel updated [{0}]
        if before.name != after.name:
            embed.add_field(name="Channel name", value=f"{before.name} → {after.name}", inline=False)
            # alert.embed.field.title.private.channel.name.updated: Channel name
            checking = True
        if before.category != after.category:
            embed.add_field(name="Cartegory name", value=f"{before.category} → {after.category}", inline=False)
            # alert.embed.field.title.private.channel.category.name.updated: Category name
            checking = True
        if before.topic != after.topic:
            embed.add_field(name="Previous Channel topic", value=f"{before.topic}", inline=True)
            # alert.embed.field.title.private.channel.previous.topic.updated: Previous Channel topic
            embed.add_field(name="Current channel topic", value=f"{after.topic}", inline=True)
            # alert.embed.field.title.private.channel.current.topic.updated: Current Channel topic
            checking = True
        if before.nsfw != after.nsfw:
            if before.nsfw:
                embed.add_field(name="NSFW", value=f"YES → NO", inline=False)
                # alert.embed.fields.title.private.channel.nsfw.updated: NSFW
            else:
                embed.add_field(name="NSFW", value=f"NO → YES", inline=False)
                # alert.embed.fields.title.private.channel.nsfw.updated: NSFW
            checking = True
        if checking:
            embed.set_footer(text="Developed by 동건#3038")
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)

        # 역할이 생성되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed = nextcord.Embed(title=f"Role created [{role.name}]", color=0x00FF22)
        # alert.embed.title.role.created: Role created [{0}]
        embed.add_field(name="ID", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```",
                        inline=False)
        # alert.embed.field.title.id: ID
        embed.set_footer(text="Developed by 동건#3038")
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=embed)

        # 역할이 삭제되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed = nextcord.Embed(title=f"<Role deleted [{role.name}]", color=0xFF0000)
        # alert.embed.title.role.deleted: Role deleted [{0}]
        embed.add_field(name="ID", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```",
                        inline=False)
        # alert.embed.field.title.id: ID
        embed.set_footer(text="Developed by 동건#3038")
        # alert.embed.footer.title: Developed by 동건#3038
        await channel.send(embed=embed)

        # 역할이 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        checking = False
        embed = nextcord.Embed(title=f"Role updated [{before.name}]", color=after.colour)
        # alert.embed.title.role.updated: Role updated [{0}]
        if before.name != after.name:
            embed.add_field(name="Name", value=f"{before.name} -> {after.name}", inline=False)
            # alert.embed.field.title.role.name: Name
            checking = True
        if before.colour != after.colour:
            embed.add_field(name="Color", value=f"{before.colour} -> {after.colour}(Same Embed color)", inline=False)
            # alert.embed.field.title.role.color: Color
            checking = True
        # 기능은 잘 작동하나,,, 역할 한개가 바뀌면 position이 모두 변경되는 바람에 쓸대없이 로그메세지를 많이 전송하여... → 주석처리 해둠
        '''
        if(before.position != after.position):
            Embed.add_field(name="순서(position)", value=f"{before.position} -> {after.position}", inline=False)
            checking = True
        '''
        if before.hoist != after.hoist:
            embed.add_field(name="Hoist", value=f"{before.hoist} -> {after.hoist}", inline=False)
            # alert.embed.field.title.role.hoist: Hoist
            checking = True
        if before.mentionable != after.mentionable:
            embed.add_field(name="Mentionable", value=f"{before.mentionable} -> {after.mentionable}", inline=False)
            checking = True
            # alert.embed.field.title.role.mentionable: Mentionable
        if checking:
            embed.add_field(name="ID", value=f"```diff\n+ {after.id} (role) \n+ {int(after.guild.id)} (guild)```",
                            inline=False)
            # alert.embed.field.title.id: ID
            embed.set_footer(text="Developed by 동건#3038")
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)

        # 유저의 서버 프로필 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        global checking
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed = nextcord.Embed(title=f"Profile(server) updated <@{after.id}>", color=0xD4FF7D)
        # alert.embed.title.server.profile.updated: Profile(server) updated <@{0}>
        checking = False
        if before.display_name != after.display_name:
            embed.add_field(name="Nickname", value=f"{before.display_name} -> {after.display_name}", inline=False)
            # alert.embed.field.title.server.profile.nickname: Nickname
            checking = True
        if checking:
            embed.add_field(name="Guild ID", value=f"```diff\n+ {int(after.guild.id)}```", inline=False)
            # alert.embed.field.title.guild.id: Guild ID
            embed.set_footer(text="Developed by 동건#3038")
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)

        # 유저의 개인 프로필 정보가 수정되었을 때, 선택된 로그채널로 로그메세지를 전송합니다.

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.get_channel(guild_manager.get_current_log_channel_id())
        embed = nextcord.Embed(title=f"Profile updated {after.id}", color=0xD4FF7D)
        # alert.embed.title.personal.profile.updated: Profile updated <@{0}>
        checking = False
        if before.name != after.name:
            embed.add_field(name="Profile name", value=f"{before.name} -> {after.name}", inline=False)
            # alert.embed.field.title.personal.profile.name: Profile name
            checking = True
        if before.discriminator != after.discriminator:
            embed.add_field(name="discriminator", value=f"{before.discriminator} -> {after.discriminator}",
                            inline=False)
            # alert.embed.field.title.personal.profile.discriminator: discriminator
            checking = True
        if before.avatar != after.avatar:
            embed.add_field(name="Profile avatar", value=f"{before.display_avatar} ```->``` {after.display_avatar}",
                            inline=False)
            # alert.embed.field.title.personal.profile.avatar: Profile avatar
            checking = True
        if checking:
            embed.add_field(name="User ID", value=f"```diff\n+ {int(after.id)} (user)```", inline=False)
            # alert.embed.field.title.user.id: User ID
            embed.set_footer(text="Developed by 동건#3038")
            # alert.embed.footer.title: Developed by 동건#3038
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Event(bot))
