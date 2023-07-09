#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2023 Lazlo Westerhof <semaphore@lazlo.me>
# Copyright (C) 2023 Shrikrishna Singh <krishnasingh.ss30@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Signal Bot examples, manage signal group actions
"""
import io
import os
import re

from semaphore import Bot, ChatContext


async def groups_list(ctx: ChatContext) -> None:
    '''Get a list of groups.'''
    groups = await ctx.bot.list_groups()
    group_list = []
    for group in groups:
        group_list.append(group.title)
    await ctx.message.reply(body=f"groups: {group_list}!")


async def group_add_members(ctx: ChatContext) -> None:
    '''Add members to a group.'''
    try:
        group_id = ctx.match.group(1)
        members = ctx.match.group(2).split(",")
    except ValueError:
        await ctx.message.reply(
            "Usage: !group add-members --groupid <group_id> --members <member_ids>"
        )
        return
    group = await ctx.bot.add_members(group_id, members)
    await ctx.message.reply(body=f"Hi {group.member_detail}!")


async def group_remove_members(ctx: ChatContext) -> None:
    '''Remove members from a group.'''
    try:
        group_id = ctx.match.group(1)
        members = ctx.match.group(2).split(",")
    except ValueError:
        await ctx.message.reply(
            "Usage: !group remove-members --groupid <group_id> --members <member_ids>"
        )
        return
    group = await ctx.bot.remove_members(group_id, members)
    await ctx.message.reply(body=f"Hi {group.member_detail}!")


async def create_group(ctx: ChatContext) -> None:
    '''Create a signal group.'''
    try:
        group_title = ctx.match.group(1)
        members = ctx.match.group(2).split(",")
    except ValueError:
        await ctx.message.reply(
            "Usage: !group create --title <group_title> --members <member_ids>"
        )
        return
    group = await ctx.bot.create_group(group_title, members)
    await ctx.message.reply(body=f"Hi {group.title}!")


async def update_group_title(ctx: ChatContext) -> None:
    '''Update title of a group.'''
    try:
        group_id = ctx.match.group(1)
        group_title = ctx.match.group(2)
    except ValueError:
        await ctx.message.reply(
            "Usage: !group update title --groupid <group_id> --newtitle <newtitlestring>"
        )
        return
    group = await ctx.bot.update_group_title(group_id, group_title)
    await ctx.message.reply(body=f"Hi {group.title}!")


async def update_group_timer(ctx: ChatContext) -> None:
    '''Update expiration timer of a group.'''
    try:
        group_id = ctx.match.group(1)
        group_timer = ctx.match.group(2)
    except ValueError:
        await ctx.message.reply(
            "Usage: !group update timer --groupid <group_id> --timer <intvalueinseconds>"
        )
        return
    group = await ctx.bot.update_group_timer(group_id, group_timer)
    await ctx.message.reply(body=f"Hi {group.timer}!")


async def update_group_role(ctx: ChatContext) -> None:
    '''Update member role for a group.'''
    try:
        group_id = ctx.match.group(1)
        member_id = ctx.match.group(2)
        role = ctx.match.group(3)
    except ValueError:
        await ctx.message.reply(
            ("Usage: !group update role --groupid <group_id>"
             " --memberid <member_id> --role <DEFAULT|ADMINSTRATION>")
        )
        return
    group = await ctx.bot.update_group_role(group_id, member_id, role)
    await ctx.message.reply(body=f"Hi {group.member_detail}!")


async def leave_group(ctx: ChatContext) -> None:
    '''Leava a group.'''
    try:
        group_id = ctx.match.group(1)
    except ValueError:
        await ctx.message.reply("Usage: !group leave <group_id>")
        return
    await ctx.bot.leave_group(group_id)


async def preview_group(ctx: ChatContext) -> None:
    '''Preview a group without joining.'''
    try:
        url = ctx.match.group(1)
    except ValueError:
        await ctx.message.reply("Usage: !group preview <group_id>")
        return
    group = await ctx.bot.preview_group(url)
    await ctx.message.reply(body=f"title: {group.title}!, {group.member_detail}")


async def group_show(ctx: ChatContext) -> None:
    '''Get information for a group.'''
    try:
        group_id = ctx.match.group(1)
    except ValueError:
        await ctx.message.reply("Usage: !group show <group_id>")
        return

    group = await ctx.bot.get_group(group_id)
    menu = io.StringIO()
    menu.write(f"id: {group.id}\n")
    menu.write(f"title: {group.title}\n")
    menu.write(f"announcements: {group.announcements}\n")
    menu.write(f"avatar: {group.avatar}\n")
    menu.write(f"description: {group.description}\n")
    menu.write(f"inviteLink: {group.inviteLink}\n")
    menu.write(f"timer: {group.timer}\n")
    menu.write(f"members: {group.member_detail}\n")
    menu.write(f"requesting_members: {group.requesting_members}")

    await ctx.message.reply(menu.getvalue())


async def main() -> None:
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler(re.compile("!group list"), groups_list)
        bot.register_handler(re.compile("!group show (.*)"), group_show)
        bot.register_handler(re.compile("!group leave (.*)"), leave_group)
        bot.register_handler(re.compile("!group preview (.*)"), preview_group)
        bot.register_handler(
            re.compile("!group add-members --groupid (.*) --members (.*)"),
            group_add_members
        )
        bot.register_handler(
            re.compile("!group remove-members --groupid (.*) --members (.*)"),
            group_remove_members
        )
        bot.register_handler(
            re.compile("!group create --title (.*) --members (.*)"),
            create_group
        )
        bot.register_handler(
            re.compile("!group update title --groupid (.*) --newtitle (.*)"),
            update_group_title
        )
        bot.register_handler(
            re.compile("!group update timer --groupid (.*) --timer (.*)"),
            update_group_timer
        )
        bot.register_handler(
            re.compile("!group update role --groupid (.*) --memberid (.*) --role (.*)"),
            update_group_role
        )

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    import anyio
    anyio.run(main)
