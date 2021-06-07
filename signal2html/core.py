# -*- coding: utf-8 -*-

"""Core functionality

License: See LICENSE file.

"""

import logging
import os
import sqlite3
import shutil
import datetime as dt

from .dbproto import StructuredMentions
from .dbproto import StructuredReaction
from .dbproto import StructuredReactions

from .addressbook import make_addressbook

from .exceptions import DatabaseNotFound
from .exceptions import DatabaseVersionNotFound

from .models import Attachment
from .models import MMSMessageRecord
from .models import Mention
from .models import Quote
from .models import Reaction
from .models import Recipient
from .models import SMSMessageRecord
from .models import Thread

from .html import dump_thread

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
        logger.warn(f"Found untested Signal database version: {version}.")
    return versioninfo


def get_color(db, recipient_id):
    """ Extract recipient color from the database """
    query = db.execute(
        "SELECT color FROM recipient_preferences WHERE recipient_ids=?",
        (recipient_id,),
    )
    color = query.fetchone()[0]
    return color


def get_sms_records(db, thread, addressbook):
    """ Collect all the SMS records for a given thread """
    sms_records = []
    sms_qry = db.execute(
        "SELECT _id, address, date, date_sent, body, type "
        "FROM sms WHERE thread_id=?",
        (thread._id,),
    )
    qry_res = sms_qry.fetchall()
    for _id, address, date, date_sent, body, _type in qry_res:
        sms_auth = addressbook.get_recipient_by_address(address)
        sms = SMSMessageRecord(
            _id=_id,
            data=None,
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
    """ Get the absolute path of an attachment, warn if it doesn't exist"""
    fname = f"Attachment_{_id}_{unique_id}.bin"
    source = os.path.abspath(os.path.join(backup_dir, fname))
    if not os.path.exists(source):
        logger.warn(
            f"Couldn't find attachment '{source}'. Maybe it was deleted or never downloaded."
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
    """ Add all attachment objects to MMS message """
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


def get_mms_mentions(encoded_mentions, addressbook, mid):
    """Decode mentions encoded in a SQL blob."""
    mentions = {}
    if encoded_mentions:
        try:
            structured_mentions = StructuredMentions.loads(encoded_mentions)
        except (ValueError, IndexError, TypeError) as e:
            logger.warn(
                f"Failed to load quote mentions for message {mid}: {str(e)}"
            )
            return []

        for structured_mention in structured_mentions.mentions:
            recipient = addressbook.get_recipient_by_uuid(
                structured_mention.who_uuid
            )
            name = recipient.name
            mention = Mention(
                mention_id=-1, name=name, length=structured_mention.length
            )
            range_start = (
                0
                if structured_mention.start is None
                else structured_mention.start
            )
            mentions[range_start] = mention

    return mentions


def get_mms_reactions(encoded_reactions, addressbook, mid):
    """Decode reactions encoded in a SQL blob."""
    reactions = []
    if encoded_reactions:
        try:
            structured_reactions = StructuredReactions.loads(encoded_reactions)
        except (ValueError, IndexError, TypeError) as e:
            logger.warn(
                f"Failed to load reactions for message {mid}: {str(e)}"
            )
            return []

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
    """ Collect all MMS records for a given thread """
    mms_records = []

    reaction_expr = versioninfo.get_reactions_query_column()

    quote_mentions_expr = versioninfo.get_quote_mentions_query_column()

    qry = db.execute(
        "SELECT _id, address, date, date_received, body, quote_id, "
        f"quote_author, quote_body, {quote_mentions_expr}, msg_box, {reaction_expr} FROM mms WHERE thread_id=?",
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

        mms_auth = addressbook.get_recipient_by_address(address)
        mms = MMSMessageRecord(
            _id=_id,
            data=None,
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


def populate_thread(
    db, thread, addressbook, backup_dir, thread_dir, versioninfo=None
):
    """ Populate a thread with all corresponding messages """
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


def process_backup(backup_dir, output_dir):
    """ Main functionality to convert database into HTML """

    # Verify backup and open database
    versioninfo = check_backup(backup_dir)
    db_file = os.path.join(backup_dir, "database.sqlite")
    db_conn = sqlite3.connect(db_file)
    db = db_conn.cursor()

    # Get and index all contact and group names
    addressbook = make_addressbook(db, versioninfo)

    # Start by getting the Threads from the database
    query = db.execute("SELECT _id, recipient_ids FROM thread")
    threads = query.fetchall()

    # Combine the recipient objects and the thread info into Thread objects
    for (_id, recipient_id) in threads:
        recipient = addressbook.get_recipient_by_address(recipient_id)
        if recipient is None:
            logger.warn(f"No recipient with address {recipient_id}")

        t = Thread(_id=_id, recipient=recipient)
        thread_dir = os.path.join(output_dir, t.sanename)
        populate_thread(
            db, t, addressbook, backup_dir, thread_dir, versioninfo=versioninfo
        )
        dump_thread(t, thread_dir)

    db.close()
