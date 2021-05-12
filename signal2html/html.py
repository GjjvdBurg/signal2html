# -*- coding: utf-8 -*-

"""Code for writing out the HTML

License: See LICENSE file.

"""

import os
import datetime as dt

from emoji import emoji_lis as emoji_list
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from .html_colors import COLORMAP
from .models import MMSMessageRecord
from .types import get_named_message_type
from .types import is_inbox_type
from .types import is_incoming_call
from .types import is_joined_type
from .types import is_missed_call
from .types import is_outgoing_call


def is_all_emoji(body):
    """ Check if a message is non-empty and only contains emoji """
    body = body.replace(" ", "").replace("\ufe0f", "")
    return len(emoji_list(body)) == len(body) and len(body) > 0


def format_message(body, is_quote=False):
    """Format message by processing all characters.

    - Wrap emoji in <span> for styling them
    - Escape special HTML chars
    """
    emoji_pos = emoji_list(body)
    new_body = ""
    emoji_lookup = {p["location"]: p["emoji"] for p in emoji_pos}
    skip = 0
    for i, c in enumerate(body):
        if skip > 0:
            # Skip additional characters from multi-character emoji
            skip = skip - 1
        elif i in emoji_lookup:
            new_body += "<span class='msg-emoji'>%s</span>" % emoji_lookup[i]
            skip = len(emoji_lookup[i]) - 1
        elif c == "&":
            new_body += "&amp;"
        elif c == "<":
            new_body += "&lt;"
        elif c == ">":
            new_body += "&gt;"
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
    msg_css = ".msg-sender-%i { /* recipient id: %5s */ background: %s;}\n"
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
            group_color_css += msg_css % (
                idx,
                ar.rid,
                COLORMAP[ar_color],
            )
            colors_used.append(ar.color)
    else:
        # Retrieve sender info from an incoming message, if any
        firstInbox = next(
            (m for m in messages if is_inbox_type(m._type)), None
        )
        if firstInbox:
            clr = firstInbox.addressRecipient.color
            clr = "teal" if clr is None else clr
            group_color_css += msg_css % (
                0,
                firstInbox.addressRecipient.rid,
                COLORMAP[clr],
            )

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
            quote_author_id = msg.quote.author.rid
            quote_author_name = msg.quote.author.name
            if quote_author_id == quote_author_name:
                name = "You"
            else:
                name = quote_author_name
            quote = {
                "name": name,
                "body": format_message(msg.quote.text),
                "attachments": [],
            }

        # Clean up message body
        body = "" if msg.body is None else msg.body
        if isinstance(msg, MMSMessageRecord):
            all_emoji = not msg.quote and is_all_emoji(body)
        else:
            all_emoji = is_all_emoji(body)
        body = format_message(body)

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

    # Use phone number to distinguish threads from the same contact,
    # except for groups, which do not have a phone number.
    filename = os.path.join(
        output_dir,
        f"{thread.sanename if is_group else thread.sanephone}.html",
    )
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write(html)
