#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extraction classes for Signal protocol objects.

These classes are used to extract values in the database encoded as protobuf messages.

Signal protobuf definitions are defined in these directories:

    https://github.com/signalapp/Signal-Android/tree/master/libsignal/service/src/main/proto
    https://github.com/signalapp/Signal-Android/tree/master/app/src/main/proto

License: See LICENSE file.
"""

from dataclasses import dataclass
from enum import IntEnum

from typing import List
from typing import Optional

from pure_protobuf.dataclasses_ import field
from pure_protobuf.dataclasses_ import message
from pure_protobuf.dataclasses_ import optional_field
from pure_protobuf.types import uint32
from pure_protobuf.types import uint64


@message
@dataclass
class StructuredReaction:
    what: str = optional_field(1)
    who: Optional[uint64] = optional_field(2)
    time_sent: Optional[uint64] = optional_field(3)
    time_received: Optional[uint64] = optional_field(4)


@message
@dataclass
class StructuredReactions:
    reactions: List[StructuredReaction] = field(1, default_factory=list)


@message
@dataclass
class StructuredMention:
    start: uint32 = optional_field(1)
    length: uint32 = optional_field(2)
    who_uuid: str = optional_field(3)


@message
@dataclass
class StructuredMentions:
    mentions: List[StructuredMention] = field(1, default_factory=list)


@message
@dataclass
class StructuredGroupCall:
    by: str = optional_field(2)
    when: uint64 = optional_field(3)


@message
@dataclass
class StructuredGroupMember:
    uuid: str = optional_field(1)
    phone: str = optional_field(2)


@message
@dataclass
class StructuredGroupDataV1:
    group_name: str = optional_field(3)
    phone_members: List[str] = field(4, default_factory=list)
    members: List[StructuredGroupMember] = field(6, default_factory=list)


class StructuredMemberRole(IntEnum):
    MEMBER_ROLE_UNKNOWN = 0
    MEMBER_ROLE_DEFAULT = 1
    MEMBER_ROLE_ADMIN = 2


@message
@dataclass
class StructuredDecryptedMember:
    uuid: bytes = field(1)
    role: StructuredMemberRole = field(2)


@message
@dataclass
class StructuredDecryptedString:
    value: str = field(1)


@message
@dataclass
class StructuredGroupV2Change:
    by: bytes = optional_field(1)
    new_members: List[StructuredDecryptedMember] = field(
        3, default_factory=list
    )
    deleted_members: List[bytes] = field(4, default_factory=list)
    new_title: StructuredDecryptedString = optional_field(10)


@message
@dataclass
class StructuredGroupV2State:
    title: str = optional_field(2)
    rev: uint32 = optional_field(6)
    members: List[StructuredDecryptedMember] = field(7, default_factory=list)


@message
@dataclass
class StructuredGroupDataV2:
    change: StructuredGroupV2Change = optional_field(2)
    state: StructuredGroupV2State = optional_field(3)
