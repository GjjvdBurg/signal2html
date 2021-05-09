# -*- coding: utf-8 -*-

"""Core functionality

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2020, G.J.J. van den Burg

"""

import logging
import os
import sqlite3
import shutil

from .addressbook import make_addressbook

from .exceptions import DatabaseNotFound
from .exceptions import DatabaseVersionNotFound

from .models import Attachment
from .models import MMSMessageRecord
from .models import Quote
from .models import Recipient
from .models import SMSMessageRecord
from .models import Thread

from .html import dump_thread

logger = logging.getLogger(__name__)


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
    if not version in ["18", "23", "65", "80", "89"]:
        logger.warn(f"Found untested Signal database version: {version}.")
    return version


def get_color(db, recipient_id):
    """ Extract recipient color from the database """
    query = db.execute(
        "SELECT color FROM recipient_preferences WHERE recipient_ids=?",
        (recipient_id,),
    )
    color = query.fetchone()[0]
    return color


def get_sms_records(db, thread, addressbook, version=None):
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


def get_mms_records(
    db, thread, addressbook, backup_dir, thread_dir, version=None
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
            quote_auth = addressbook.get_recipient_by_address(quote_author)
            quote = Quote(_id=quote_id, author=quote_auth, text=quote_body)

        mms_auth = addressbook.get_recipient_by_address(address)
        mms = MMSMessageRecord(
            _id=_id,
            addressRecipient=mms_auth,
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
    db, thread, addressbook, backup_dir, thread_dir, version=None
):
    """ Populate a thread with all corresponding messages """
    sms_records = get_sms_records(db, thread, addressbook, version=version)
    mms_records = get_mms_records(
        db, thread, addressbook, backup_dir, thread_dir, version=version
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

    # Get and index all contact and group names
    addressbook = make_addressbook(db, db_version)

    # Start by getting the Threads from the database
    query = db.execute("SELECT _id, recipient_ids FROM thread")
    threads = query.fetchall()

    # Combine the recipient objects and the thread info into Thread objects
    for (_id, recipient_id) in threads:
        recipient = addressbook.get_recipient_by_address(recipient_id)
        if recipient is None:
            print(f"No recipient with address {recipient_id}")

        t = Thread(_id=_id, recipient=recipient)
        thread_dir = os.path.join(output_dir, t.sanename)
        populate_thread(
            db, t, addressbook, backup_dir, thread_dir, version=db_version
        )
        dump_thread(t, thread_dir)

    db.close()
