# -*- coding: utf-8 -*-

"""Core functionality

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2020, G.J.J. van den Burg

"""

import inspect
import os
import warnings
import sqlite3
import shutil

from .exceptions import DatabaseNotFound
from .exceptions import DatabaseVersionNotFound

from .models import Attachment
from .models import MMSMessageRecord
from .models import Quote
from .models import Recipient
from .models import RecipientId
from .models import SMSMessageRecord
from .models import Thread

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
    if not version in ["23", "65", "80", "89"]:
        warnings.warn(
            f"Warning: Found untested Signal database version: {version}."
        )
    return version


def make_group_dict(db, version):
    groups = {}
    qry = db.execute("SELECT group_id, title FROM groups")
    qry_res = qry.fetchall()
    for group_id, title in qry_res:
        groups[group_id] = title

    return groups


def make_addressbook_v23(db, version, groups_by_id, rid_to_recipient):
    qry = db.execute(
        "SELECT recipient_ids, system_display_name, color "
        "FROM recipient_preferences "
    )
    qry_res = qry.fetchall()
    for recipient_id, system_display_name, color in qry_res:
        if recipient_id.startswith("__textsecure_group__"):
            name = groups_by_id.get(recipient_id)
            isgroup = True
            if name is None:
                warnings.warn(
                    f"Group for recipient {recipient_id} does not exist."
                )
        else:
            name = system_display_name
            isgroup = False

        recipient_id = RecipientId(str(recipient_id))

        if name is None:
            name = ""

        if color is None:
            color = get_random_color()

        rid_to_recipient[str(recipient_id)] = Recipient(
            recipient_id, name=name, color=color, isgroup=isgroup, phone=""
        )


def make_addressbook_v80(
    db, version, groups_by_id, rid_to_recipient, phone_to_rid
):
    qry = db.execute(
        "SELECT _id, group_id, "
        "phone, "
        "system_display_name, "
        "profile_joined_name, "
        "color "
        "FROM recipient "
    )
    qry_res = qry.fetchall()
    for (
        recipient_id,
        group_id,
        phone,
        name,
        profile_joined_name,
        color,
    ) in qry_res:
        isgroup = group_id is not None
        if isgroup:
            name = groups_by_id.get(group_id)
            if name is None:
                warnings.warn(
                    f"Group for recipient {recipient_id} is {group_id} which does not exist."
                )

        rid = RecipientId(str(recipient_id))

        if name is None:
            if profile_joined_name:
                name = profile_joined_name
            elif phone:
                name = phone
            else:
                name = ""

        if color is None:
            color = get_random_color()

        rid_to_recipient[str(recipient_id)] = Recipient(
            rid, name=name, color=color, isgroup=isgroup, phone=phone
        )
        if phone:
            phone_to_rid[phone] = str(recipient_id)


def make_addressbook(
    db, version, groups_by_id, rid_to_recipient, phone_to_rid
):
    if version == "23":
        return make_addressbook_v23(
            db, version, groups_by_id, rid_to_recipient
        )
    elif version in ["65", "80", "89"]:
        return make_addressbook_v80(
            db, version, groups_by_id, rid_to_recipient, phone_to_rid
        )

    return make_addressbook_v80(
        db, groups_by_id, version, rid_to_recipient, phone_to_rid
    )


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
            "SELECT system_display_name "
            "FROM recipient_preferences "
            "WHERE recipient_ids=?",
            (recipient_id,),
        )
        label = qry.fetchone()
        isgroup = False

    name = str(recipient_id) if label[0] is None else label[0]
    color = get_color(db, recipient_id)

    phone = str(recipient_id)
    rid = RecipientId(recipient_id)
    return Recipient(rid, name=name, color=color, isgroup=isgroup, phone=phone)


def make_recipient_v80(db, recipient_id):
    """Create a Recipient instance from a recipient id (db version 65, 80, 89)"""
    qry = db.execute(
        "SELECT group_id, "
        "phone, "
        "system_display_name, "
        "profile_joined_name, "
        "color "
        "FROM recipient "
        "WHERE _id=?",
        (recipient_id,),
    )
    group_id, phone, name, joined_name, color = qry.fetchone()
    if color is None:
        color = get_random_color()

    isgroup = group_id is not None
    if isgroup:
        qry = db.execute(
            "SELECT title FROM groups WHERE group_id=?", (group_id,)
        )
        res = qry.fetchone()
        if res is not None:
            name = res[0]
        else:
            warnings.warn(
                f"Group for recipient {recipient_id} is {group_id} which does not exist."
            )

    if name is None:
        if joined_name:
            name = joined_name
        elif phone:
            name = phone
        else:
            name = ""

    rid = RecipientId(recipient_id)
    return Recipient(rid, name=name, color=color, isgroup=isgroup, phone=phone)


def make_recipient(db, recipient_id, version=None):
    warnings.warn(
        f"Call to deprecated function {inspect.stack()[0][3]} from {inspect.stack()[1][3]}."
    )
    if version == "23":
        return make_recipient_v23(db, recipient_id)
    elif version in ["65", "80", "89"]:
        return make_recipient_v80(db, recipient_id)

    warnings.warn(
        f"Untested database version {version}, defaulting to latest known working version."
    )
    return make_recipient_v80(db, recipient_id)


def get_sms_records(db, thread, recipients, version=None):
    """ Collect all the SMS records for a given thread """
    sms_records = []
    sms_qry = db.execute(
        "SELECT _id, address, date, date_sent, body, type "
        "FROM sms WHERE thread_id=?",
        (thread._id,),
    )
    qry_res = sms_qry.fetchall()
    for _id, address, date, date_sent, body, _type in qry_res:
        sms_auth = recipients.get(address)
        sms = SMSMessageRecord(
            _id=_id,
            addressRecipient=sms_auth
            if sms_auth
            else make_recipient(db, address, version=version),
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
            quote_auth = recipients.get(quote_author)
            if quote_auth is None:
                # Quote is from someone who isn't a recipient (e.g. a friend
                # quotes a third person in a group). We'll just create a
                # recipient object for this person.
                rid = RecipientId(quote_author)
                quote_auth = Recipient(
                    rid,
                    quote_author,
                    color=None,
                    isgroup=False,
                    phone=str(quote_author),
                )
            quote = Quote(_id=quote_id, author=quote_auth, text=quote_body)

        mms_auth = recipients.get(address)
        mms = MMSMessageRecord(
            _id=_id,
            addressRecipient=mms_auth
            if mms_auth
            else make_recipient(db, address, version=version),
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
    sms_records = get_sms_records(db, thread, recipients, version=version)
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

    # Get and index all contact names
    groups_by_id = make_group_dict(db, version=db_version)
    rid_to_recipient: dict(str, Recipient) = {}
    phone_to_rid: dict(str, str) = {}

    addressbook_by_rid = make_addressbook(
        db, db_version, groups_by_id, rid_to_recipient, phone_to_rid
    )

    # Start by getting the Threads from the database
    query = db.execute("SELECT _id, recipient_ids FROM thread")
    threads = query.fetchall()

    # Combine the recipient objects and the thread info into Thread objects
    for (_id, recipient_id) in threads:
        recipient = rid_to_recipient[recipient_id]
        t = Thread(_id=_id, recipient=recipient)
        thread_dir = os.path.join(output_dir, t.sanename)
        populate_thread(
            db, t, rid_to_recipient, backup_dir, thread_dir, version=db_version
        )
        dump_thread(t, thread_dir)

    db.close()
