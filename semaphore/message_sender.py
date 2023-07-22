#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2023 Lazlo Westerhof <semaphore@lazlo.me>
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
"""This module contains a class that handles sending bot messages."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from .exceptions import IDENTIFIABLE_SIGNALD_ERRORS, UnknownError
from .groupV2 import GroupV2
from .message import Message
from .profile import Profile
from .reply import Reply
from .socket import Socket

if TYPE_CHECKING:
    from .attachment import Attachment
    from .link_preview import LinkPreview


class MessageSender:
    """This class handles sending bot messages."""
    signald_message_id: int = 0

    def __init__(self, username: str, socket: Socket, raise_errors: bool = False):
        """Initialize message sender."""
        self._username: str = username
        self._socket: Socket = socket
        self._raise_signald_errors = raise_errors
        self._socket_lock = asyncio.Lock()
        self.log = logging.getLogger(__name__)

    async def _send(self, message: Dict) -> Any:
        if message['type'] == 'send':
            self.signald_message_id += 1
            message['id'] = str(self.signald_message_id)

        async with self._socket_lock:
            await self._socket.send(message)

            # Wait on response for our message.
            if message.get('id'):
                self.log.debug(f"Waiting for success of message id {message['id']}")
            # Wait on responses for several types of messages.
            elif message.get('type') == 'get_profile':
                self.log.debug("Waiting for response of get_profile")
            elif message.get('type') == 'get_group':
                self.log.debug("Waiting for response of get_group")
            elif message.get('type') == 'list_groups':
                self.log.debug("Waiting for response of list_groups")
            elif message.get('type') == 'update_group':
                self.log.debug("Waiting for response of update_group")
            elif message.get('type') == 'create_group':
                self.log.debug("Waiting for response of create_group")
            elif message.get('type') == 'leave_group':
                self.log.debug("Waiting for response of leave_group")
            elif message.get('type') == 'group_link_info':
                self.log.debug("Waiting for response of preview_group")
            # Skip everything else.
            else:
                return True

            # Wait for response.
            async for line in self._socket.read():
                self.log.debug(f"Socket of sender received: {line.decode()}")

                # Load Signal message wrapper.
                try:
                    response_wrapper = json.loads(line)
                except json.JSONDecodeError as e:
                    self.log.error("Could not decode signald response", exc_info=e)
                    continue

                # Return get_profile response.
                if response_wrapper.get('type') == 'get_profile':
                    return Profile.create_from_receive_dict(
                        response_wrapper.get('data', {})
                    )

                if response_wrapper.get('type') == 'list_groups':
                    return [
                        GroupV2.create_from_receive_dict(
                            group
                        ) for group in response_wrapper.get('data', {})['groups']
                    ]

                if response_wrapper.get('type') == 'get_group':
                    return GroupV2.create_from_receive_dict(
                        response_wrapper.get('data', {})
                    )

                if response_wrapper.get('type') == 'update_group':
                    return GroupV2.create_from_receive_dict(
                        response_wrapper.get('data', {})['v2']
                    )

                if response_wrapper.get('type') == 'create_group':
                    return GroupV2.create_from_receive_dict(
                        response_wrapper.get('data', {})
                    )

                if response_wrapper.get('type') == 'leave_group':
                    return GroupV2.create_from_receive_dict(
                        response_wrapper.get('data', {})
                    )

                if response_wrapper.get('type') == 'group_link_info':
                    return GroupV2.create_from_receive_dict(
                        response_wrapper.get('data', {})
                    )

                # Skip everything but response for our message.
                if 'id' not in response_wrapper:
                    continue

                if response_wrapper['id'] != message['id']:
                    self.log.warning("Received message response for another id")
                    continue

                if response_wrapper.get("error") is not None:
                    self.log.warning(f"Could not send message:"
                                     f"{response_wrapper}")

                    if not self._raise_signald_errors:
                        return False

                    # Match error.
                    for error_class in IDENTIFIABLE_SIGNALD_ERRORS:
                        if error_class.IDENTIFIER == response_wrapper.get("error_type"):
                            error_dict = response_wrapper.get("error")
                            if not error_dict:
                                break

                            error = error_class()
                            for k in error_dict.keys():
                                setattr(error, k, error_dict.get(k))

                            raise error

                    raise UnknownError(response_wrapper.get("error_type"),
                                       response_wrapper.get("error"))

                response = response_wrapper['data']
                results = response.get("results")

                if results:
                    if results[0].get('success'):
                        return True
                return False
            return False

    async def send_message(self, receiver: str, body: str,
                           attachments: Optional[List[Attachment]] = None,
                           link_previews: Optional[List[LinkPreview]] = None) -> bool:
        """
        Send a message.

        :param receiver:      The receiver of the message (uuid or number).
        :param body:          The body of the message.
        :param attachments:   Optional attachments to the message.
        :param link_previews: Optional link previews for the message.

        :return: Returns whether sending is successful.
        :rtype: bool
        """
        bot_message: Dict[str, Union[str, Dict[str, str], List[Dict[str, str]]]] = {
            "type": "send",
            "version": "v1",
            "username": self._username,
            "messageBody": body
        }

        if receiver[-1] == "=":
            bot_message["recipientGroupId"] = receiver
        elif re.search(r"\+\d*", receiver):
            bot_message["recipientAddress"] = {"number": receiver}
        else:
            bot_message["recipientAddress"] = {"uuid": receiver}

        # Add attachments to message.
        if attachments:
            bot_message["attachments"] = [
                attachment.to_send_dict() for attachment in attachments
            ]

        if link_previews:
            bot_message["previews"] = [
                link_preview.to_send_dict() for link_preview in link_previews
            ]

        return await self._send(bot_message)

    async def reply_message(self, message: Message, reply: Reply) -> bool:
        """
        Send the bot message.

        :param message: The original message replying to.
        :param reply:   The reply to send.

        :return: Returns whether replying is successful.
        :rtype: bool
        """
        # Mark message as read before replying.
        if reply.mark_read:
            await message.mark_read()

        # Construct reply message.
        bot_message: Dict[str, Any] = {}
        if reply.reaction:
            bot_message = {
                "type": "react",
                "version": "v1",
                "username": self._username,
                "reaction": {
                    "emoji": reply.body,
                    "targetAuthor": {"uuid": message.source.uuid},
                    "targetSentTimestamp": message.timestamp
                }
            }
        else:
            bot_message = {
                "type": "send",
                "version": "v1",
                "username": self._username,
                "messageBody": reply.body
            }

            # Add attachments to message.
            if reply.attachments:
                bot_message["attachments"] = [
                    attachment.to_send_dict() for attachment in reply.attachments
                ]

            if reply.link_previews:
                bot_message["previews"] = [
                    link_preview.to_send_dict() for link_preview in reply.link_previews
                ]

            # Add quote to message.
            if reply.quote:
                quote = {"id": message.timestamp,
                         "author": {'uuid': message.source.uuid},
                         "text": message.get_body()}
                bot_message["quote"] = quote

        # Add message recipient.
        if message.get_group_id():
            bot_message["recipientGroupId"] = message.get_group_id()
        else:
            bot_message["recipientAddress"] = {"uuid": message.source.uuid}

        return await self._send(bot_message)

    async def typing_started(self, message: Message) -> None:
        """
        Send a typing started message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing",
                                          "version": "v1",
                                          "typing": True,
                                          "account": self._username}

        # Add group id or address.
        if message.get_group_id():
            typing_message["group"] = message.get_group_id()
        else:
            typing_message["address"] = {"uuid": message.source.uuid}

        await self._send(typing_message)

    async def typing_stopped(self, message: Message) -> None:
        """
        Send a typing stopped message.

        :param message: The Signal message you received.
        """
        # Construct reply message.
        typing_message: Dict[str, Any] = {"type": "typing",
                                          "version": "v1",
                                          "typing": False,
                                          "account": self._username}

        # Add group id or address.
        if message.get_group_id():
            typing_message["group"] = message.get_group_id()
        else:
            typing_message["address"] = {"uuid": message.source.uuid}

        await self._send(typing_message)

    async def mark_read(self, message: Message) -> None:
        """
        Mark a Signal message you received as read.

        :param message: The Signal message you received.
        """
        await self._send({
            "type": "mark_read",
            "version": "v1",
            "account": self._username,
            "to": {"uuid": message.source.uuid},
            "timestamps": [message.timestamp],
        })

    async def set_profile(self,
                          profile_name: str,
                          profile_avatar: Optional[str] = None,
                          profile_emoji: Optional[str] = None,
                          profile_about: Optional[str] = None) -> None:
        """
        Set Signal profile.

        :param profile_name:   New profile name, empty string for no profile name.
        :param profile_avatar: Path to profile avatar file.
        :param profile_emoji:  Emoji character visible in profile.
        :param profile_about:  Description text visible in profile.
        """
        profile_message = {"type": "set_profile",
                           "version": "v1",
                           "account": self._username,
                           "name": profile_name}

        if profile_avatar:
            profile_message["avatarFile"] = profile_avatar

        if profile_emoji:
            profile_message["emoji"] = profile_emoji

        if profile_about:
            profile_message["about"] = profile_about

        await self._send(profile_message)

    async def get_profile(self, message: Message) -> Profile:
        """
        Get Signal profile of message sender.

        :param message: The Signal message you received.

        :returns: Signal profile
        """
        return await self._send({
            "type": "get_profile",
            "version": "v1",
            "account": self._username,
            "address": {"uuid": message.source.uuid}
        })

    async def set_expiration(self, receiver: str, time: int) -> None:
        """
        Set the message expiration timer for a chat.

        :param receiver: The receiver for which to set the expiration time.
        :param time:     Time must be specified in seconds, set to 0 to disable timer.
        """
        expiration_message = {"type": "set_expiration",
                              "version": "v1",
                              "account": self._username,
                              "expiration": time}

        if receiver[-1] == "=":
            expiration_message["group"] = receiver
        elif re.search(r"\+\d*", receiver):
            expiration_message["address"] = {"number": receiver}
        else:
            expiration_message["address"] = {"uuid": receiver}

        await self._send(expiration_message)

    async def accept_invitation(self, group_id: str) -> None:
        """
        Accept a group invitation.

        :param group_id: Group id to accept invitation from
        """
        await self._send({
            "type": "accept_invitation",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
        })

    async def list_groups(self) -> List[GroupV2]:
        """
        List groups for an account.

        :return: Returns a list of v2 group objects
        """
        return await self._send({
            "type": "list_groups",
            "version": "v1",
            "account": self._username,
        })

    async def get_group(self, group_id: str) -> GroupV2:
        """
        Get details of a group.

        :param group_id: Group id to get details for

        :return: Returns a GroupV2 object
        """
        return await self._send({
            "type": "get_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
        })

    async def add_members(self, group_id: str, members: list) -> GroupV2:
        """
        Add members to a group.

        :param group_id: Group id to add the members to
        :param members:  List of members uuids to be added

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "addMembers": members,
        })

    async def remove_members(self, group_id: str, members: list) -> GroupV2:
        """
        Remove members from a group.

        :param group_id: Group id to remove the members from
        :param members:  List of members uuids to be removed

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "removeMembers": members,
        })

    async def create_group(self, title: str, members: list) -> GroupV2:
        """
        Create a Signal group.

        :param title:   Title for the new group.
        :param members: List of members uuids to be added to the new group

        :return: Returns the created GroupV2 object
        """
        return await self._send({
            "type": "create_group",
            "version": "v1",
            "account": self._username,
            "title": title,
            "members": members
        })

    async def leave_group(self, group_id: str) -> GroupV2:
        """
        Leave a Signal group.

        :param group_id: Identifier of the group to leave

        :return: Returns a GroupV2 object
        """
        return await self._send({
            "type": "leave_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
        })

    async def preview_group(self, url: str) -> GroupV2:
        """
        Preview information about a group without joining.

        :param url: Group invite link to preview information for

        :return: Returns a GroupV2 object
        """
        return await self._send({
            "type": "group_link_info",
            "version": "v1",
            "account": self._username,
            "uri": url,
        })

    async def update_group_title(self, group_id: str, title: str) -> GroupV2:
        """
        Update a group’s title.

        :param group_id: Identifier of the group to update the title for
        :param title:    New title

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "title": title,
        })

    async def update_group_timer(self, group_id: str, timer: str) -> GroupV2:
        """
        Update a group’s timer.

        :param group_id: Identifier of the group to change timer of
        :param timer:    Expiration must be specified in seconds, 0 to disable timer

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "updateTimer": timer,
        })

    async def update_group_role(self,
                                group_id: str,
                                member_id: str,
                                role: str) -> GroupV2:
        """
        Update the role of a member in the group.

        :param group_id:  Identifier of the group to update member role for
        :param member_id: Identifier of the member
        :param role:      Updated role of the member

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "updateRole": {
                'role': role,
                'uuid': member_id
            }
        })

    async def update_group_avatar(self, group_id: str, group_avatar: str) -> GroupV2:
        """
        Change a group’s avatar.

        :param group_id:     Identifier of the group to update avatar for
        :param group_avatar: Path to group avatar file

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "avatar": group_avatar,
        })

    async def update_group_access_control(self,
                                          group_id: str,
                                          access_control: str,
                                          role: str) -> GroupV2:
        """
        Change a group’s access control.

        :param group_id:       Identifier of the group to update avatar for
        :param access_control: Name of the access control,
                               options are: attributes|members|link
        :param role:           Set the role of an access control:
                               for attributes otions are: UNSATISFIABLE|ADMINISTRATOR|ANY
                               for members otions are: MEMBER|ADMINISTRATOR
                               for link options are: MEMBER|ADMINISTRATOR

        :return: Returns the updated GroupV2 object
        """
        return await self._send({
            "type": "update_group",
            "version": "v1",
            "account": self._username,
            "groupID": group_id,
            "updateAccessControl": {
                access_control: role
            },
        })
