# -*- coding: utf-8 -*-

"""Code for writing out the HTML

Author: Gertjan van den Burg

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
    """ Check if a message is non-empty and only contains emoji """
    body = body.replace(" ", "").replace("\ufe0f", "")
    return len(emoji_list(body)) == len(body) and len(body) > 0


def format_emoji(body, is_quote=False):
    """ Wrap emoji in <span> so we can style it easily """
    emoji_pos = emoji_list(body)
    new_body = ""
    emoji_lookup = {p["location"]: p["emoji"] for p in emoji_pos}
    for i, c in enumerate(body):
        if i in emoji_lookup:
            new_body += "<span class='msg-emoji'>%s</span>" % emoji_lookup[i]
        else:
            new_body += c
    return new_body


def dump_thread(thread, output_dir):
    """Write a Thread instance to a HTML page in the output directory """

    # Combine and sort the messages
    messages = thread.mms + thread.sms
    messages.sort(key=lambda mr: mr.dateSent)

    # Find the template
    env = Environment(
        loader=PackageLoader("signal2html", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("thread.html")

    is_group = thread.recipient.isgroup

    # Create the message color CSS (depends on individuals)
    group_color_css = ""
    msg_css = ".msg-sender-%i { background: %s; }\n"
    if is_group:
        group_recipients = set(m.addressRecipient for m in messages)
        sender_idx = {r: k for k, r in enumerate(group_recipients)}
        colors_used = []
        group_colors = set(ar.color for ar in sender_idx)
        for ar, idx in sender_idx.items():
            if ar.isgroup:
                continue

            # ensure colors are unique, even if they're not in Signal
            ar_color = ar.color
            if ar_color in colors_used:
                color = next(
                    (c for c in COLORMAP if not c in group_colors),
                    None,
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

        # Add a "date change" message when to mark the date
        date_sent = dt.datetime.fromtimestamp(msg.dateSent // 1000)
        date_sent = date_sent.replace(microsecond=(msg.dateSent % 1000) * 1000)
        if prev_date is None or date_sent.date() != prev_date:
            prev_date = date_sent.date()
            out = {
                "date_msg": True,
                "body": date_sent.strftime("%a, %b %d, %Y"),
            }
            simple_messages.append(out)

        # Handle calls
        is_call = False
        if is_incoming_call(msg._type):
            is_call = True
            msg.body = f"{thread.name} called you"
        elif is_outgoing_call(msg._type):
            is_call = True
            msg.body = "You called"
        elif is_missed_call(msg._type):
            is_call = True
            msg.body = "Missed call"

        # Deal with quoted messages
        quote = {}
        if isinstance(msg, MMSMessageRecord) and msg.quote:
            quote_author_id = msg.quote.author.recipientId._id
            quote_author_name = msg.quote.author.name
            if quote_author_id == quote_author_name:
                name = "You"
            else:
                name = quote_author_name
            quote = {
                "name": name,
                "body": format_emoji(msg.quote.text),
                "attachments": [],
            }

        # Clean up message body
        body = "" if msg.body is None else msg.body
        if isinstance(msg, MMSMessageRecord):
            all_emoji = not msg.quote and is_all_emoji(body)
        else:
            all_emoji = is_all_emoji(body)
        body = format_emoji(body)

        # Create message dictionary
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
            "name": aR.name,
            "sender_idx": sender_idx[aR] if is_group else "0",
            "quote": quote,
        }

        # Add attachments
        if isinstance(msg, MMSMessageRecord):
            for a in msg.attachments:
                if a.quote:
                    out["quote"]["attachments"].append(a)
                else:
                    out["attachments"].append(a)

        simple_messages.append(out)

    if not simple_messages:
        return

    html = template.render(
        thread_name=thread.name,
        messages=simple_messages,
        group_color_css=group_color_css,
    )

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(
        output_dir, thread.name.replace(" ", "_") + ".html"
    )
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write(html)
