# -*- coding: utf-8 -*-

"""Utilities for dealing with message types

These are extracted from the Signal Android app source code.

License: See LICENSE file.

"""

from enum import Enum

BASE_TYPE_MASK = 0x1F

INCOMING_AUDIO_CALL_TYPE = 1
OUTGOING_AUDIO_CALL_TYPE = 2
MISSED_AUDIO_CALL_TYPE = 3
JOINED_TYPE = 4
UNSUPPORTED_MESSAGE_TYPE = 5
INVALID_MESSAGE_TYPE = 6
MISSED_VIDEO_CALL_TYPE = 8
INCOMING_VIDEO_CALL_TYPE = 10
OUTGOING_VIDEO_CALL_TYPE = 11
GROUP_CALL_TYPE = 12

KEY_UPDATE_TYPE_BIT = 0x200

GROUP_CTRL_TYPE_BIT = 0x10000
GROUP_V2_DATA_TYPE_BIT = 0x80000

SECURE_BIT = 0x800000

BASE_INBOX_TYPE = 20
BASE_OUTBOX_TYPE = 21
BASE_SENDING_TYPE = 22
BASE_SENT_TYPE = 23
BASE_SENT_FAILED_TYPE = 24
BASE_PENDING_SECURE_SMS_FALLBACK = 25
BASE_PENDING_INSECURE_SMS_FALLBACK = 26
BASE_DRAFT_TYPE = 27

OUTGOING_MESSAGE_TYPES = [
    BASE_OUTBOX_TYPE,
    BASE_SENT_TYPE,
    BASE_SENDING_TYPE,
    BASE_SENT_FAILED_TYPE,
    BASE_PENDING_SECURE_SMS_FALLBACK,
    BASE_PENDING_INSECURE_SMS_FALLBACK,
]


class DisplayType(Enum):
    DISPLAY_TYPE_NONE = 0
    DISPLAY_TYPE_PENDING = 1
    DISPLAY_TYPE_SENT = 2
    DISPLAY_TYPE_FAILED = 3
    DISPLAY_TYPE_DELIVERED = 4
    DISPLAY_TYPE_READ = 5

    @classmethod
    def from_state(
        cls, _type: int, is_delivered: bool = False, is_read: bool = False
    ):
        if not is_outgoing_message_type(_type):
            return cls.DISPLAY_TYPE_NONE

        if is_read:
            return cls.DISPLAY_TYPE_READ

        if is_delivered:
            return cls.DISPLAY_TYPE_DELIVERED

        base_type = _type & BASE_TYPE_MASK

        if base_type == BASE_SENT_FAILED_TYPE:
            return cls.DISPLAY_TYPE_FAILED

        if base_type == BASE_SENT_TYPE:
            return cls.DISPLAY_TYPE_SENT

        if (
            base_type == BASE_OUTBOX_TYPE
            or base_type == BASE_SENDING_TYPE
            or base_type == BASE_PENDING_SECURE_SMS_FALLBACK
            or base_type == BASE_PENDING_INSECURE_SMS_FALLBACK
        ):
            return cls.DISPLAY_TYPE_PENDING

        return cls.DISPLAY_TYPE_NONE


def is_outgoing_message_type(_type):
    for outgoingType in OUTGOING_MESSAGE_TYPES:
        if _type & BASE_TYPE_MASK == outgoingType:
            return True
    return False


def is_inbox_type(_type):
    return _type & BASE_TYPE_MASK == BASE_INBOX_TYPE


def is_incoming_call(_type):
    return _type in (INCOMING_AUDIO_CALL_TYPE, INCOMING_VIDEO_CALL_TYPE)


def is_outgoing_call(_type):
    return _type in (OUTGOING_AUDIO_CALL_TYPE, OUTGOING_VIDEO_CALL_TYPE)


def is_missed_call(_type):
    return _type in (MISSED_AUDIO_CALL_TYPE, MISSED_VIDEO_CALL_TYPE)


def is_video_call(_type):
    return _type in (
        INCOMING_VIDEO_CALL_TYPE,
        OUTGOING_VIDEO_CALL_TYPE,
        MISSED_VIDEO_CALL_TYPE,
    )


def is_group_call(_type):
    return _type == GROUP_CALL_TYPE


def is_key_update(_type):
    return _type & KEY_UPDATE_TYPE_BIT == KEY_UPDATE_TYPE_BIT


def is_secure(_type):
    return _type & SECURE_BIT == SECURE_BIT


def is_group_ctrl(_type):
    return _type & GROUP_CTRL_TYPE_BIT == GROUP_CTRL_TYPE_BIT


def is_group_v2_data(_type):
    return _type & GROUP_V2_DATA_TYPE_BIT == GROUP_V2_DATA_TYPE_BIT


def is_joined_type(_type):
    return _type & BASE_TYPE_MASK == JOINED_TYPE


def get_named_message_type(_type):
    if is_group_ctrl(_type):
        if is_group_v2_data(_type):
            return "group-update-v2"
        else:
            return "group-update-v1"
    elif is_key_update(_type):
        return "key-update"
    elif is_outgoing_message_type(_type):
        return "outgoing"
    elif is_inbox_type(_type):
        return "incoming"
    elif is_incoming_call(_type):
        return (
            "video-call-incoming" if is_video_call(_type) else "call-incoming"
        )
    elif is_outgoing_call(_type):
        return (
            "video-call-outgoing" if is_video_call(_type) else "call-outgoing"
        )
    elif is_missed_call(_type):
        return "video-call-missed" if is_video_call(_type) else "call-missed"
    elif is_group_call(_type):
        return "group-call"
    elif is_joined_type(_type):
        return "joined"
    return "unknown"
