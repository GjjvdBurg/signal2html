# -*- coding: utf-8 -*-

"""Core functionality

Author: Gertjan van den Burg

"""

import os
import warnings
import sqlite3
import shutil

from .exceptions import (
    DatabaseNotFound,
    DatabaseVersionNotFound,
)
from .models import (
    Attachment,
    MMSMessageRecord,
    Quote,
    Recipient,
    RecipientId,
    SMSMessageRecord,
    Thread,
)
from .html import dump_thread
from .html_colors import get_random_color


def check_backup(backup_dir):
    """Check that we have the necessary files"""
    if not os.path.join(backup_dir, "database.sqlite"):
        raise DatabaseNotFound
    if not os.path.join(backup_dir, "DatabaseVersion.sbf"):
        raise DatabaseVersionNotFound
    with open(os.path.join(backup_dir, "DatabaseVersion.sbf"), "r") as fp:
        version_str = fp.read()

    # We have only ever seen database version 23, so we don't proceed if it's
    # not that. Testing and pull requests welcome.
    version = version_str.split(":")[-1].strip()
    if not version in ["23", "65", "80"]:
        warnings.warn(
            f"Warning: Found untested Signal database version: {version}."
        )
    return version


def get_color(db, recipient_id):
    """ Extract recipient color from the database """
    query = db.execute(
        "SELECT color FROM recipient_preferences WHERE recipient_ids=?",
        (recipient_id,),
    )
    color = query.fetchone()[0]
    return color


def make_recipient_v23(db, recipient_id):
    """ Create a Recipient instance from a given recipient id (db version 23)"""
    if recipient_id.startswith("__textsecure_group__"):
        qry = db.execute(
            "SELECT title FROM groups WHERE group_id=?", (recipient_id,)
        )
        label = qry.fetchone()
        isgroup = True
    else:
        qry = db.execute(
            "SELECT system_display_name FROM recipient_preferences WHERE recipient_ids=?",
            (recipient_id,),
        )
        label = qry.fetchone()
        isgroup = False

    name = str(recipient_id) if label[0] is None else label[0]
    color = get_color(db, recipient_id)

    rid = RecipientId(recipient_id)
    return Recipient(rid, name=name, color=color, isgroup=isgroup)


def make_recipient_v80(db, recipient_id):
    """Create a Recipient instance from a recipient id (db version 65, 80)"""
    qry = db.execute(
        "SELECT group_id, system_display_name, profile_joined_name, color from recipient where _id=?",
        (recipient_id,),
    )
    groupid, name, joined_name, color = qry.fetchone()
    if color is None:
        color = get_random_color()

    isgroup = groupid is not None
    if isgroup:
        qry = db.execute(
            "SELECT title FROM groups WHERE group_id=?", (groupid,)
        )
        name = qry.fetchone()[0]

    if name is None:
        if joined_name is None:
            name = str(recipient_id)
        else:
            name = joined_name

    rid = RecipientId(recipient_id)
    return Recipient(rid, name=name, color=color, isgroup=isgroup)


def make_recipient(db, recipient_id, version=None):
    if version == "23":
        return make_recipient_v23(db, recipient_id)
    elif version in ["65", "80"]:
        return make_recipient_v80(db, recipient_id)
    else:
        warnings.warn(
            f"Untested database version {version}, defaulting to latest known working version."
        )
        return make_recipient_v80(db, recipient_id)


def get_sms_records(db, thread, version=None):
    """ Collect all the SMS records for a given thread """
    sms_records = []
    sms_qry = db.execute(
        "SELECT _id, address, date, date_sent, body, type "
        "FROM sms WHERE thread_id=?",
        (thread._id,),
    )
    qry_res = sms_qry.fetchall()
    for _id, address, date, date_sent, body, _type in qry_res:
        sms = SMSMessageRecord(
            _id=_id,
            addressRecipient=make_recipient(db, address, version=version),
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
        warnings.warn(
            f"Warning: couldn't find attachment {source}. Maybe it was deleted?"
        )
        return None

    # Copying here is a bit of a side-effect
    target_dir = os.path.abspath(os.path.join(thread_dir, "attachments"))
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, fname)
    shutil.copy(source, target)
    return target


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


def get_mms_records(
    db, thread, recipients, backup_dir, thread_dir, version=None
):
    """ Collect all MMS records for a given thread """
    mms_records = []
    qry = db.execute(
        "SELECT _id, address, date, date_received, body, quote_id, "
        "quote_author, quote_body, msg_box FROM mms WHERE thread_id=?",
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
        msg_box,
    ) in qry_res:
        quote = None
        if quote_id:
            quote_auth = next(
                (
                    r
                    for r in recipients
                    if str(r.recipientId._id) == str(quote_author)
                ),
                None,
            )
            if quote_auth is None:
                # Quote is from someone who isn't a recipient (e.g. a friend
                # quotes a third person in a group). We'll just create a
                # recipient object for this person.
                rid = RecipientId(quote_author)
                quote_auth = Recipient(
                    rid, quote_author, color=None, isgroup=False
                )
            quote = Quote(_id=quote_id, author=quote_auth, text=quote_body)

        mms = MMSMessageRecord(
            _id=_id,
            addressRecipient=make_recipient(db, address, version=version),
            recipient=thread.recipient,
            dateSent=date,
            dateReceived=date_received,
            threadId=thread._id,
            body=body,
            quote=quote,
            attachments=[],
            _type=msg_box,
        )
        mms_records.append(mms)

    for mms in mms_records:
        add_mms_attachments(db, mms, backup_dir, thread_dir)

    return mms_records


def populate_thread(
    db, thread, recipients, backup_dir, thread_dir, version=None
):
    """ Populate a thread with all corresponding messages """
    sms_records = get_sms_records(db, thread, version=version)
    mms_records = get_mms_records(
        db, thread, recipients, backup_dir, thread_dir, version=version
    )
    thread.sms = sms_records
    thread.mms = mms_records


def process_backup(backup_dir, output_dir):
    """ Main functionality to convert database into HTML """

    # Verify backup and open database
    db_version = check_backup(backup_dir)
    db_file = os.path.join(backup_dir, "database.sqlite")
    db_conn = sqlite3.connect(db_file)
    db = db_conn.cursor()

    # Start by getting the Threads from the database
    query = db.execute("SELECT _id, recipient_ids FROM thread")
    threads = query.fetchall()

    # Now turn the recipients from the threads into Recipient classes
    recipients = []
    for _, recipient_id in threads:
        r = make_recipient(db, recipient_id, version=db_version)
        recipients.append(r)

    # Combine the recipient objects and the thread info into Thread objects
    for (_id, _), recipient in zip(threads, recipients):
        t = Thread(_id=_id, recipient=recipient)
        thread_dir = os.path.join(output_dir, t.name.replace(" ", "_"))
        populate_thread(
            db, t, recipients, backup_dir, thread_dir, version=db_version
        )
        dump_thread(t, thread_dir)

    db.close()
