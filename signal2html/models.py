# -*- coding: utf-8 -*-

"""
Models for storing Signal backup objects.

These are heavily inspired by the database models of the Signal Android app, 
but only the necessary fields are kept.

License: See LICENSE file.

"""

import os

from abc import ABCMeta
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from re import sub
from unicodedata import normalize

from typing import Dict
from typing import List


@dataclass
class Recipient:
    rid: int
    name: str
    color: str
    isgroup: bool
    phone: str
    uuid: str

    def __hash__(self):
        return hash(self.rid)


@dataclass
class Mention:
    mention_id: int
    name: str
    length: int


@dataclass
class Quote:
    _id: int
    author: Recipient
    text: str
    mentions: Dict[int, Mention] = field(default_factory=lambda: {})


@dataclass
class Attachment:
    contentType: str
    fileName: str
    voiceNote: bool
    width: int
    height: int
    quote: bool
    unique_id: str


@dataclass
class GroupCallData:
    initiator: str
    timestamp: datetime


@dataclass
class MemberInfo:
    name: str
    phone: str
    match_from_phone: bool
    admin: bool


@dataclass
class GroupUpdateData:
    group_name: str
    change_by: MemberInfo
    members: List[MemberInfo] = field(default_factory=list)
    new_members: List[MemberInfo] = field(default_factory=list)
    deleted_members: List[MemberInfo] = field(default_factory=list)


@dataclass
class DisplayRecord(metaclass=ABCMeta):
    addressRecipient: Recipient  # Recipient corresponding to address field
    recipient: Recipient
    dateSent: int
    dateReceived: int
    threadId: int
    body: str
    _type: int


@dataclass
class MessageRecord(DisplayRecord):
    _id: int
    data: any
    delivery_receipt_count: int
    read_receipt_count: int


@dataclass
class Reaction:
    recipient: Recipient
    what: str
    time_sent: datetime
    time_received: datetime


@dataclass
class MMSMessageRecord(MessageRecord):
    quote: Quote
    attachments: List[Attachment]
    reactions: List[Reaction]
    viewed_receipt_count: int


@dataclass
class SMSMessageRecord(MessageRecord):
    pass


@dataclass
class Thread:
    _id: int
    recipient: Recipient
    mms: List[MMSMessageRecord] = field(default_factory=lambda: [])
    sms: List[SMSMessageRecord] = field(default_factory=lambda: [])
    mentions: Dict[int, Dict[int, Mention]] = field(default_factory=lambda: {})
    members: List[Recipient] = field(default_factory=lambda: [])

    @property
    def is_group(self) -> bool:
        return self.recipient.isgroup

    @property
    def sanephone(self):
        """Return a sanitized phone number suitable for use as filename, and fallback on rid.

        NOTE: Phone numbers can be alphanumerical characters especially coming over SMS
        Different strings can still clash in principle if they sanitize to the same string.
        """
        if self.recipient.phone:
            return self._sanitize(self.recipient.phone)
        return "#" + str(self.recipient.rid)

    @property
    def name(self):
        """Return the raw name or other useful identifier, suitable for display."""
        return self.recipient.name.strip()

    @property
    def sanename(self):
        """Return a sanitized name or other useful identifier, suitable for use
        as filename, and fallback on rid."""
        if self.recipient.name:
            return self._sanitize(self.recipient.name)
        return "#" + str(self.recipient.rid)

    def _sanitize(self, text):
        """Sanitize text to use as filename"""
        clean = normalize("NFKC", text.strip())
        clean = clean.lstrip(".#")
        clean = sub("[^]\\w!@#$%^&'`.=+{}~()[-]", "_", clean)
        clean = clean.rstrip("_")
        return clean

    def get_thread_dir(self, output_dir: str, make_dir=True) -> str:
        return os.path.dirname(self.get_path(output_dir, make_dir=make_dir))

    def get_path(self, output_dir: str, make_dir=True) -> str:
        """Return a path for a thread and try to be clever about merging
        contacts. Optionally create the contact directory."""
        dirname = self.sanename
        # Use phone number to distinguish threads from the same contact,
        # except for groups, which do not have a phone number.
        filename = f"{self.sanename if self.is_group else self.sanephone}.html"
        path = os.path.join(output_dir, dirname, filename)
        i = 2
        while os.path.exists(path):
            if self.is_group:
                dirname = f"{self.sanename}_{i}"
            else:
                filename = f"{self.sanephone}_{i}.html"
            path = os.path.join(output_dir, dirname, filename)
            i += 1
        if make_dir:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
