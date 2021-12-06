#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2021 Lazlo Westerhof <semaphore@lazlo.me>
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
"""This module contains exceptions for Semaphore."""
from typing import Dict, List, Optional


class StopPropagation(Exception):
    """Raise this to prevent further handlers from running on this message."""


class SignaldError(Exception):
    """This is the base class for Signald Errors"""
    IDENTIFIER: str

    pass


class NoSuchAccountError(SignaldError):
    IDENTIFIER = "NoSuchAccountError"

    account: str
    message: str


class SeverNotFoundError(SignaldError):
    IDENTIFIER = "SeverNotFoundError"

    message: str
    uuid: str


class InvalidProxyError(SignaldError):
    IDENTIFIER = "InvalidProxyError"

    message: str


class NoSendPermissionError(SignaldError):
    IDENTIFIER = "NoSendPermissionError"

    message: str


class InvalidAttachmentError(SignaldError):
    IDENTIFIER = "InvalidAttachmentError"

    filename: str
    message: str


class InternalError(SignaldError):
    IDENTIFIER = "InternalError"

    exceptions: List[str]
    message: str


class IllegalArgumentException(SignaldError):
    IDENTIFIER = "IllegalArgumentException"

    message: str
    stackTraceDepth: int


class InvalidRequestError(SignaldError):
    IDENTIFIER = "InvalidRequestError"

    message: str


class UnknownGroupError(SignaldError):
    IDENTIFIER = "UnknownGroupError"

    message: str


class RateLimitError(SignaldError):
    IDENTIFIER = "RateLimitError"

    message: str


class InvalidRecipientError(SignaldError):
    IDENTIFIER = "InvalidRecipientError"

    message: str


class UnknownError(SignaldError):
    """Exception raised if send did return an error that is
    not implemented in semaphore"""
    error: Optional[Dict]
    error_type: str

    def __init__(self, error_type: str, error_object: Optional[Dict]):
        self.error_type = error_type
        self.error = error_object


IDENTIFIABLE_SIGNALD_ERRORS = [NoSuchAccountError, SeverNotFoundError, InvalidProxyError,
                               NoSendPermissionError, InvalidAttachmentError,
                               InternalError, IllegalArgumentException,
                               InvalidRequestError, UnknownGroupError, RateLimitError,
                               InvalidRecipientError]
