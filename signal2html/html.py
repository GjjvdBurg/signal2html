# -*- coding: utf-8 -*-

"""Code for writing out the HTML

"""

import os
import datetime as dt

from emoji import emoji_lis as emoji_list
from jinja2 import Environment, PackageLoader, select_autoescape

from .models import MMSMessageRecord
from .types import (
    get_named_message_type,
    is_inbox_type,
    is_incoming_call,
    is_joined_type,
    is_missed_call,
    is_outgoing_call,
)
from .html_colors import COLORMAP


def is_all_emoji(body):
    body = body.replace(" ", "").replace("\ufe0f", "")
    return len(emoji_list(body)) == len(body)


def dump_thread(thread, output_dir):
    # Combine and sort the messages
    messages = thread.mms + thread.sms
    messages.sort(key=lambda mr: mr.dateSent)

    # Find the template
    env = Environment(
        loader=PackageLoader("signal2html", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("thread.html")

    # Get thread name and determine if group
    thread_name = thread.recipient.name[0].strip()
    is_group = False
    if thread.recipient.recipientId._id.startswith("__textsecure_group__"):
        is_group = True

    # Create the message color CSS (depends on individuals)
    group_color_css = ""
    msg_css = ".msg-sender-%i { background: %s; }\n"
    if is_group:
        group_recipients = set(m.addressRecipient for m in messages)
        sender_idx = {r: k for k, r in enumerate(group_recipients)}
        colors_used = []
        group_colors = set(ar.color for ar in sender_idx)
        for ar, idx in sender_idx.items():
            if ar.recipientId._id.startswith("__textsecure_group__"):
                continue
            # ensure colors are unique, even if they're not in Signal
            ar_color = ar.color
            if ar_color in colors_used:
                color = next(
                    (c for c in COLORMAP if not c in group_colors), None,
                )
                ar_color = ar.color if color is None else color
            group_color_css += msg_css % (idx, COLORMAP[ar_color])
            colors_used.append(ar.color)
    else:
        firstInbox = next(
            (m for m in messages if is_inbox_type(m._type)), None
        )
        clr = firstInbox.addressRecipient.color if firstInbox else "teal"
        clr = "teal" if clr is None else clr
        group_color_css += msg_css % (0, COLORMAP[clr])

    # Create a simplified dict for each message
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

        body = "" if msg.body is None else msg.body
        all_emoji = is_all_emoji(body)
        emoji_pos = emoji_list(body)
        new_body = ""
        emoji_lookup = {p["location"]: p["emoji"] for p in emoji_pos}
        for i, c in enumerate(body):
            if i in emoji_lookup:
                new_body += (
                    "<span class='msg-emoji'>%s</span>" % emoji_lookup[i]
                )
            else:
                new_body += c
        body = new_body

        aR = msg.addressRecipient
        out = {
            "isAllEmoji": all_emoji,
            "isGroup": is_group,
            "isCall": is_call,
            "type": get_named_message_type(msg._type),
            "body": body,
            "date": date_sent,
            "attachments": [],
            "id": msg._id,
            "name": aR.name[0],
            "sender_idx": sender_idx[aR] if is_group else "0",
        }

        if isinstance(msg, MMSMessageRecord):
            out["attachments"] = msg.attachments
        simple_messages.append(out)

    if not simple_messages:
        return

    html = template.render(
        thread_name=thread_name,
        messages=simple_messages,
        group_color_css=group_color_css,
    )

    filename = os.path.join(
        output_dir, thread_name.replace(" ", "_") + ".html"
    )
    with open(filename, "w") as fp:
        fp.write(html)
