#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extraction classes for Signal protocol objects.

These classes are used to extract values in the database encoded as protobuf messages.

License: See LICENSE file.
"""

from dataclasses import dataclass
from typing import List, Optional
from pure_protobuf.dataclasses_ import field, message, optional_field
from pure_protobuf.types import uint32, uint64


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
