# -*- coding: utf-8 -*-

"""Code for writing out the HTML

"""

import os
import datetime as dt

from jinja2 import Environment, PackageLoader, select_autoescape

from .models import MMSMessageRecord
from .types import (
    get_named_message_type,
    is_joined_type,
    is_outgoing_call,
    is_missed_call,
    is_incoming_call,
)


def dump_thread(thread, output_dir):
    messages = thread.mms + thread.sms
    messages.sort(key=lambda mr: mr.dateSent)

    env = Environment(
        loader=PackageLoader("signal2html", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("thread.html")

    thread_name = thread.recipient.name[0].strip()
    is_group = False
    if thread.recipient.recipientId._id.startswith("__textsecure_group__"):
        is_group = True

    prev_date = None
    simple_messages = []
    for msg in messages:
        if is_joined_type(msg._type):
            continue

        date_sent = dt.datetime.fromtimestamp(msg.dateSent // 1000)
        date_sent = date_sent.replace(microsecond=(msg.dateSent % 1000) * 1000)
        if prev_date is None or date_sent.date() != prev_date:
            prev_date = date_sent.date()
            out = {
                "date_msg": True,
                "body": date_sent.strftime("%a, %b %d, %Y"),
            }
            simple_messages.append(out)

        is_call = False
        if is_incoming_call(msg._type):
            is_call = True
            msg.body = f"{thread_name} called you"
        elif is_outgoing_call(msg._type):
            is_call = True
            msg.body = "You called"
        elif is_missed_call(msg._type):
            is_call = True
            msg.body = "Missed call"

        out = {
            "isGroup": is_group,
            "isCall": is_call,
            "type": get_named_message_type(msg._type),
            "body": "" if msg.body is None else msg.body,
            "date": date_sent,
            "attachments": [],
            "id": msg._id,
            "name": msg.addressRecipient.name[0],
        }

        if isinstance(msg, MMSMessageRecord):
            out["attachments"] = msg.attachments
        simple_messages.append(out)

    if not simple_messages:
        return

    html = template.render(thread_name=thread_name, messages=simple_messages)

    filename = os.path.join(
        output_dir, thread_name.replace(" ", "_") + ".html"
    )
    with open(filename, "w") as fp:
        fp.write(html)


def dump_index():
    pass
