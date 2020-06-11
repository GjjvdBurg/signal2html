# -*- coding: utf-8 -*-

"""Code for writing out the HTML

"""

import os

from jinja2 import Environment, PackageLoader, select_autoescape

from .types import get_named_message_type, is_joined_type


def dump_thread(thread, output_dir):
    messages = thread.mms + thread.sms
    messages.sort(key=lambda mr: mr.dateSent)

    env = Environment(
        loader=PackageLoader("signalbrowse", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("thread.html")

    thread_name = thread.recipient.name[0].strip()

    simple_messages = []
    for msg in messages:
        if is_joined_type(msg._type):
            continue
        out = {
            "type": get_named_message_type(msg._type),
            "body": "" if msg.body is None else msg.body,
        }
        simple_messages.append(out)

    if not simple_messages:
        return

    html = template.render(thread_name=thread_name, messages=simple_messages)

    filename = os.path.join(output_dir, thread_name.replace(' ', '_') + 
            ".html")
    with open(filename, "w") as fp:
        fp.write(html)


def dump_index():
    pass
