#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models for storing Signal backup objects.

These are heavily inspired by the database models of the Signal Android app, 
but only the necessary fields are kept.

Author: Gertjan van den Burg

"""

from abc import ABCMeta
from dataclasses import dataclass, field
from typing import List


@dataclass
class RecipientId:
    _id: str  # phone number (?)

    def __hash__(self):
        return hash(self._id)


@dataclass
class Quote:
    _id: int
    author: RecipientId
    text: str


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
class Recipient:
    recipientId: RecipientId
    name: str
    color: str
    isgroup: bool

    def __hash__(self):
        return hash(self.recipientId)


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


@dataclass
class MMSMessageRecord(MessageRecord):
    quote: Quote
    attachments: List[Attachment]


@dataclass
class SMSMessageRecord(MessageRecord):
    pass


@dataclass
class Thread:
    _id: int
    recipient: Recipient
    mms: List[MMSMessageRecord] = field(default_factory=lambda: [])
    sms: List[SMSMessageRecord] = field(default_factory=lambda: [])

    @property
    def name(self):
        return self.recipient.name.strip()
