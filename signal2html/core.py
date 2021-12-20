# -*- coding: utf-8 -*-

"""Core functionality

License: See LICENSE file.

"""

import base64
import binascii
import datetime as dt
import logging
import os
import shutil
import sqlite3
import uuid

from typing import List

from .__version__ import __version__
from .addressbook import Addressbook
from .addressbook import make_addressbook
from .dbproto import StructuredGroupCall
from .dbproto import StructuredGroupDataV1
from .dbproto import StructuredGroupDataV2
from .dbproto import StructuredMemberRole
from .dbproto import StructuredMentions
from .dbproto import StructuredReactions
from .exceptions import DatabaseNotFound
from .exceptions import DatabaseVersionNotFound
from .html import dump_thread
from .models import Attachment
from .models import GroupCallData
from .models import GroupUpdateData
from .models import MemberInfo
from .models import Mention
from .models import MMSMessageRecord
from .models import Quote
from .models import Reaction
from .models import Recipient
from .models import SMSMessageRecord
from .models import Thread
from .types import is_group_call
from .types import is_group_ctrl
from .types import is_group_v2_data
from .versioninfo import VersionInfo

logger = logging.getLogger(__name__)


def check_backup(backup_dir) -> VersionInfo:
    """Check that we have the necessary files and return VersionInfo"""
    if not os.path.join(backup_dir, "database.sqlite"):
        raise DatabaseNotFound
    if not os.path.join(backup_dir, "DatabaseVersion.sbf"):
        raise DatabaseVersionNotFound
    with open(os.path.join(backup_dir, "DatabaseVersion.sbf"), "r") as fp:
        version_str = fp.read()

    version = version_str.split(":")[-1].strip()
    versioninfo = VersionInfo(version)

    if not versioninfo.is_tested_version():
        logger.warn(
            f"This database version is untested, please report errors."
        )
    return versioninfo


def get_color(db, recipient_id):
    """Extract recipient color from the database"""
    query = db.execute(
        "SELECT color FROM recipient_preferences WHERE recipient_ids=?",
        (recipient_id,),
    )
    color = query.fetchone()[0]
    return color


def get_sms_records(db, thread, addressbook):
    """Collect all the SMS records for a given thread"""
    sms_records = []
    sms_qry = db.execute(
        "SELECT _id, address, date, date_sent, body, type, "
        "delivery_receipt_count, read_receipt_count "
        "FROM sms WHERE thread_id=?",
        (thread._id,),
    )
    qry_res = sms_qry.fetchall()
    for (
        _id,
        address,
        date,
        date_sent,
        body,
        _type,
        delivery_receipt_count,
        read_receipt_count,
    ) in qry_res:

        data = get_data_from_body(_type, body, addressbook, _id)
        sms_auth = addressbook.get_recipient_by_address(str(address))
        sms = SMSMessageRecord(
            _id=_id,
            data=data,
            delivery_receipt_count=delivery_receipt_count,
            read_receipt_count=read_receipt_count,
            addressRecipient=sms_auth,
            recipient=thread.recipient,
            dateSent=date_sent,
            dateReceived=date,
            threadId=thread._id,
            body=body,
            _type=_type,
        )
        sms_records.append(sms)
    return sms_records


def get_attachment_filename(_id, unique_id, backup_dir, thread_dir):
    """Get the absolute path of an attachment, warn if it doesn't exist"""
    fname = f"Attachment_{_id}_{unique_id}.bin"
    source = os.path.abspath(os.path.join(backup_dir, fname))
    if not os.path.exists(source):
        logger.warn(
            f"Couldn't find attachment '{source}'. "
            "Maybe it was deleted or never downloaded?"
        )
        return None

    # Copying here is a bit of a side-effect
    target_dir = os.path.abspath(os.path.join(thread_dir, "attachments"))
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, fname)
    shutil.copy(source, target)
    url = "/".join([".", "attachments", fname])
    return url


def add_mms_attachments(db, mms, backup_dir, thread_dir):
    """Add all attachment objects to MMS message"""
    qry = db.execute(
        "SELECT _id, ct, unique_id, voice_note, width, height, quote "
        "FROM part WHERE mid=?",
        (mms._id,),
    )
    for _id, ct, unique_id, voice_note, width, height, quote in qry:
        a = Attachment(
            contentType=ct,
            unique_id=unique_id,
            fileName=get_attachment_filename(
                _id, unique_id, backup_dir, thread_dir
            ),
            voiceNote=voice_note,
            width=width,
            height=height,
            quote=quote,
        )
        mms.attachments.append(a)


def decode_body(body):
    """Decode a base64-encoded message body."""
    try:
        return base64.b64decode(body)
    except (TypeError, ValueError, binascii.Error) as e:
        logger.warn(f"Failed to decode body for message '{body}': {str(e)}")
        return None


def get_group_call_data(rawbody, addressbook, mid):
    """Get the data for a group call."""

    if not rawbody:
        return None

    try:
        structured_call = StructuredGroupCall.loads(rawbody)
    except (ValueError, IndexError, TypeError) as e:
        logger.warn(
            f"Failed to load group call data for message {mid}:\n"
            f"Error message: {str(e)}"
        )
        return None

    timestamp = dt.datetime.fromtimestamp(structured_call.when // 1000)
    timestamp = timestamp.replace(
        microsecond=(structured_call.when % 1000) * 1000
    )
    recipient = addressbook.get_recipient_by_uuid(structured_call.by)
    if recipient:
        initiator = recipient.name

    group_call_data = GroupCallData(
        initiator=initiator,
        timestamp=timestamp,
    )

    return group_call_data


def get_group_update_data_v1(rawbody, addressbook, mid):
    """Get the data for a Group V1 update.

    There are two lists of members:
    - One list by structures with telephone numbers and/or UUIDs
    - Another list by telephone numbers

    Some groups use the first (sometimes without filling the UUID field),
    some use the second, and some both.

    Merge both lists and indicate for each member if they were found by phone
    or by UUID (preferable)."""

    if not rawbody:
        return None

    try:
        structured_group_data = StructuredGroupDataV1.loads(rawbody)
    except (ValueError, IndexError, TypeError) as e:
        logger.warn(
            f"Failed to load group update data (v1) for message {mid}:\n"
            f"Error message: {str(e)}"
        )
        return None

    members = dict()
    for member in structured_group_data.members:
        name = None
        match_from_phone = False
        if member.uuid:
            name = addressbook.get_recipient_by_uuid(member.uuid).name
        elif member.phone:
            name = addressbook.get_recipient_by_phone(member.phone).name
            match_from_phone = True

        member_info = MemberInfo(
            name=name,
            phone=member.phone,
            match_from_phone=match_from_phone,
            admin=False,
        )
        members[member.phone] = member_info

    for phone_member in structured_group_data.phone_members:
        if not members.get(phone_member):
            name = addressbook.get_recipient_by_phone(phone_member).name
            member_info = MemberInfo(
                name=name,
                phone=phone_member,
                match_from_phone=True,
                admin=False,
            )
            members[phone_member] = member_info

    members_list = list()
    for key, value in members.items():
        members_list.append(value)

    group_update_data = GroupUpdateData(
        group_name=structured_group_data.group_name,
        change_by=None,
        members=members_list,
    )
    return group_update_data


def get_member_by_raw_uuid(raw_uuid: bytes, what: str, addressbook, mid: str):
    """Find a recipient from a binary UUID. Output their name from the
    addressbook or the textual UUID if not found."""

    try:
        text_uuid = str(uuid.UUID(bytes=raw_uuid))
    except ValueError as e:
        logger.warn(f"Failed to parse {what} UUID for message {mid}: {str(e)}")
        return None

    recipient = addressbook.get_recipient_by_uuid(text_uuid)
    member_name = recipient.name if recipient else text_uuid
    return member_name


def get_group_update_data_v2(rawbody, addressbook, mid):
    """Get the data for a Group V2 update.

    Group V2 updates use UUIDs exclusively to identify members. The update
    messages contain the old state, the new state, and a description of the
    changes. Parse the change description to print out:
    - The person who made the change (editor)
    - A new group name
    - Added (new) members
    - Deleted members

    Also parse the new state to print out the resulting list of members."""

    if not rawbody:
        return None

    try:
        structured_group_data = StructuredGroupDataV2.loads(rawbody)
    except (ValueError, IndexError, TypeError) as e:
        logger.warn(
            f"Failed to load group update data (v2) for message {mid}:\n"
            f"Error message: {str(e)}"
        )
        return None

    change = structured_group_data.change
    deleted_members = []
    new_members = []
    members = []
    change_by = None
    editor = None
    if (not change is None) and (not change.by is None):
        editor = get_member_by_raw_uuid(
            change.by, "update editor", addressbook, mid
        )
        if editor:
            change_by = MemberInfo(
                name=editor,
                phone=None,
                match_from_phone=False,
                admin=False,
            )

    for member in change.new_members:
        name = (
            get_member_by_raw_uuid(member.uuid, "new member", addressbook, mid)
            or "Unknown"
        )
        admin = member.role == StructuredMemberRole.MEMBER_ROLE_ADMIN
        new_members.append(
            MemberInfo(
                name=name, phone=None, match_from_phone=False, admin=admin
            )
        )

    for member in change.deleted_members:
        name = (
            get_member_by_raw_uuid(member, "deleted member", addressbook, mid)
            or "Unknown"
        )
        deleted_members.append(
            MemberInfo(
                name=name, phone=None, match_from_phone=False, admin=False
            )
        )

    state = structured_group_data.state
    for member in state.members:
        name = (
            get_member_by_raw_uuid(member.uuid, "member", addressbook, mid)
            or "Unknown"
        )
        admin = member.role == StructuredMemberRole.MEMBER_ROLE_ADMIN
        members.append(
            MemberInfo(
                name=name, phone=None, match_from_phone=False, admin=admin
            )
        )

    group_update_data = GroupUpdateData(
        group_name=change.new_title.value if change.new_title else None,
        change_by=change_by,
        members=members,
        new_members=new_members,
        deleted_members=deleted_members,
    )
    return group_update_data


def get_data_from_body(_type, body, addressbook, mid):
    """Decode data in the message body and provide a structured representation."""
    data = None
    if is_group_call(_type):
        data = get_group_call_data(decode_body(body), addressbook, mid)
    elif is_group_ctrl(_type):
        if is_group_v2_data(_type):
            data = get_group_update_data_v2(
                decode_body(body), addressbook, mid
            )
        else:
            data = get_group_update_data_v1(
                decode_body(body), addressbook, mid
            )

    return data


def get_mms_mentions(encoded_mentions, addressbook, mid):
    """Decode mentions encoded in a SQL blob."""
    mentions = {}
    if not encoded_mentions:
        return mentions

    try:
        structured_mentions = StructuredMentions.loads(encoded_mentions)
    except (ValueError, IndexError, TypeError) as e:
        logger.warn(
            f"Failed to load quote mentions for message {mid}:\n"
            f"Error message: {str(e)}"
        )
        return mentions

    for structured_mention in structured_mentions.mentions:
        recipient = addressbook.get_recipient_by_uuid(
            structured_mention.who_uuid
        )
        name = recipient.name
        mention = Mention(
            mention_id=-1, name=name, length=structured_mention.length
        )
        range_start = (
            0 if structured_mention.start is None else structured_mention.start
        )
        mentions[range_start] = mention

    return mentions


def get_mms_reactions(encoded_reactions, addressbook, mid):
    """Decode reactions encoded in a SQL blob."""
    reactions = []
    if not encoded_reactions:
        return reactions

    try:
        structured_reactions = StructuredReactions.loads(encoded_reactions)
    except (ValueError, IndexError, TypeError) as e:
        logger.warn(
            f"Failed to load reactions for message {mid}:\n"
            f"Error message: {str(e)}"
        )
        return reactions

    for structured_reaction in structured_reactions.reactions:
        recipient = addressbook.get_recipient_by_address(
            str(structured_reaction.who)
        )
        reaction = Reaction(
            recipient=recipient,
            what=structured_reaction.what,
            time_sent=dt.datetime.fromtimestamp(
                structured_reaction.time_sent // 1000
            ),
            time_received=dt.datetime.fromtimestamp(
                structured_reaction.time_received // 1000
            ),
        )
        reaction.time_sent = reaction.time_sent.replace(
            microsecond=(structured_reaction.time_sent % 1000) * 1000
        )
        reaction.time_received = reaction.time_received.replace(
            microsecond=(structured_reaction.time_received % 1000) * 1000
        )
        reactions.append(reaction)

    return reactions


def get_mms_records(
    db, thread, addressbook, backup_dir, thread_dir, versioninfo
):
    """Collect all MMS records for a given thread"""
    mms_records = []

    reaction_expr = versioninfo.get_reactions_query_column()
    quote_mentions_expr = versioninfo.get_quote_mentions_query_column()
    viewed_receipt_count_expr = versioninfo.get_viewed_receipt_count_column()

    qry = db.execute(
        "SELECT _id, address, date, date_received, body, quote_id, "
        f"quote_author, quote_body, {quote_mentions_expr}, msg_box, {reaction_expr}, "
        f"delivery_receipt_count, read_receipt_count, {viewed_receipt_count_expr} "
        "FROM mms WHERE thread_id=?",
        (thread._id,),
    )
    qry_res = qry.fetchall()
    for (
        _id,
        address,
        date,
        date_received,
        body,
        quote_id,
        quote_author,
        quote_body,
        quote_mentions,
        msg_box,
        reactions,
        delivery_receipt_count,
        read_receipt_count,
        viewed_receipt_count,
    ) in qry_res:
        quote = get_mms_quote(
            addressbook,
            quote_id,
            quote_author,
            quote_body,
            quote_mentions,
            _id,
        )

        decoded_reactions = get_mms_reactions(reactions, addressbook, _id)

        data = get_data_from_body(msg_box, body, addressbook, _id)
        mms_auth = addressbook.get_recipient_by_address(str(address))
        mms = MMSMessageRecord(
            _id=_id,
            data=data,
            delivery_receipt_count=delivery_receipt_count,
            read_receipt_count=read_receipt_count,
            addressRecipient=mms_auth,
            recipient=thread.recipient,
            dateSent=date,
            dateReceived=date_received,
            threadId=thread._id,
            body=body,
            quote=quote,
            attachments=[],
            reactions=decoded_reactions,
            _type=msg_box,
            viewed_receipt_count=viewed_receipt_count,
        )
        mms_records.append(mms)

    for mms in mms_records:
        add_mms_attachments(db, mms, backup_dir, thread_dir)

    return mms_records


def get_mms_quote(
    addressbook, quote_id, quote_author, quote_body, quote_mentions, mid
):
    """Retrieve quote (replied message) from a MMS message."""
    quote = None
    if quote_id:
        quote_auth = addressbook.get_recipient_by_address(quote_author)
        decoded_mentions = get_mms_mentions(quote_mentions, addressbook, mid)
        quote = Quote(
            _id=quote_id,
            author=quote_auth,
            text=quote_body,
            mentions=decoded_mentions,
        )
    return quote


def get_mentions(db, addressbook, thread_id, versioninfo):
    """Retrieve all mentions in the DB for the requested thread into a dictionary."""
    mentions = {}

    if versioninfo.are_mentions_supported():
        query = db.execute(
            "SELECT _id, message_id, recipient_id, range_start, range_length "
            "FROM mention WHERE thread_id=?",
            (thread_id,),
        )
        mentions_data = query.fetchall()

        for (
            _id,
            message_id,
            recipient_id,
            range_start,
            range_length,
        ) in mentions_data:
            name = addressbook.get_recipient_by_address(str(recipient_id)).name
            mention = Mention(
                mention_id=_id,
                name=name,
                length=range_length,
            )
            if not message_id in mentions.keys():
                mentions[message_id] = {}
            mentions[message_id][range_start] = mention

    return mentions


def get_members(
    db: sqlite3.Cursor,
    addressbook: Addressbook,
    thread_id: int,
    versioninfo: VersionInfo,
) -> List[Recipient]:
    """Retrieve the thread members from the database

    Returns
    -------
    members: List[Recipient]
        A list of Recipients for each member in the group.
    """
    thread_rid_column = versioninfo.get_thread_recipient_id_column()
    if versioninfo.is_addressbook_using_rids():
        query = db.execute(
            "SELECT r._id, g.members "
            "FROM thread t "
            "LEFT JOIN recipient r "
            f"ON t.{thread_rid_column} = r._id "
            "LEFT JOIN groups g "
            "ON g.group_id = r.group_id "
            "WHERE t._id = :thread_id",
            {"thread_id": thread_id},
        )
        query_result = query.fetchall()
        recipient_id, thread_members = query_result[0]
    else:
        query = db.execute(
            "SELECT t.recipient_ids, g.members "
            "FROM thread t "
            "LEFT JOIN groups g "
            "ON t.recipient_ids = g.group_id "
            "WHERE t._id = :thread_id",
            {"thread_id": thread_id},
        )
        query_result = query.fetchall()
        recipient_id, thread_members = query_result[0]

    if not thread_members is None:
        member_addresses = thread_members.split(",")
        members = []
        for address in member_addresses:
            recipient = addressbook.get_recipient_by_address(address)
            members.append(recipient)
    else:
        members = [addressbook.get_recipient_by_address(recipient_id)]
    return members


def populate_thread(
    db, thread, addressbook, backup_dir, thread_dir, versioninfo=None
):
    """Populate a thread with all corresponding messages"""
    sms_records = get_sms_records(db, thread, addressbook)
    mms_records = get_mms_records(
        db,
        thread,
        addressbook,
        backup_dir,
        thread_dir,
        versioninfo,
    )
    thread.sms = sms_records
    thread.mms = mms_records
    thread.mentions = get_mentions(db, addressbook, thread._id, versioninfo)
    thread.members = get_members(db, addressbook, thread._id, versioninfo)


def process_backup(backup_dir, output_dir):
    """Main functionality to convert database into HTML"""

    logger.info(f"This is signal2html version {__version__}")

    # Verify backup and open database
    versioninfo = check_backup(backup_dir)
    db_file = os.path.join(backup_dir, "database.sqlite")
    db_conn = sqlite3.connect(db_file)
    db = db_conn.cursor()

    # Get and index all contact and group names
    addressbook = make_addressbook(db, versioninfo)

    # Start by getting the Threads from the database
    recipient_id_expr = versioninfo.get_thread_recipient_id_column()

    query = db.execute(f"SELECT _id, {recipient_id_expr} FROM thread")
    threads = query.fetchall()

    # Combine the recipient objects and the thread info into Thread objects
    for (_id, recipient_id) in threads:
        recipient = addressbook.get_recipient_by_address(str(recipient_id))
        if recipient is None:
            logger.warn(f"No recipient with address {recipient_id}")

        t = Thread(_id=_id, recipient=recipient)
        thread_dir = t.get_thread_dir(output_dir, make_dir=False)
        populate_thread(
            db, t, addressbook, backup_dir, thread_dir, versioninfo=versioninfo
        )
        dump_thread(t, output_dir)

    db.close()
