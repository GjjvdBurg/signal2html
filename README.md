# signal2html: Convert Signal backups to pretty HTML

[![build](https://github.com/GjjvdBurg/signal2html/actions/workflows/build.yml/badge.svg)](https://github.com/GjjvdBurg/signal2html/actions/workflows/build.yml)
[![PyPI version](https://badge.fury.io/py/signal2html.svg)](https://pypi.org/project/signal2html)
[![Downloads](https://pepy.tech/badge/signal2html)](https://pepy.tech/project/signal2html)

This is a Python script to convert a backup of [Signal](https://signal.org/) 
messages to pretty HTML:

<p align="center">
  <img width="60%" src="https://raw.githubusercontent.com/GjjvdBurg/signal2html/ea182b6ffc2a08da19f999016d5d47cd714ce17e/screenshot.png">
</p>

## Why?

My phone was getting full and I wanted to preserve my Signal messages in a 
nice way.

## How?

1. Install this package using pip:
   ```
   $ pip install signal2html
   ```

2. Next, clone and compile 
   [signalbackup-tools](https://github.com/bepaald/signalbackup-tools) as 
   follows:
   ```
   $ git clone https://github.com/bepaald/signalbackup-tools
   $ cd signalbackup-tools
   $ bash BUILDSCRIPT.sh
   ```
   This should give you a ``signalbackup-tools`` executable script.

3. Create an encrypted backup of your Signal messages in the app (Settings -> 
   Chats and Media -> Create backup), and transfer this to your computer. Make 
   sure to record the encryption password.

4. Unpack your encrypted backup using ``signalbackup-tools`` as follows:
   ```
   $ mkdir signal-backup/
   $ signalbackup-tools --output signal_backup/ signal-YYYY-MM-DD-HH-MM-SS.backup <PASS>
   ```
   where you replace ``signal-YYYY-MM-DD-HH-MM-SS.backup`` with the actual 
   filename of your Signal backup and ``<PASS>`` with the 30-digit encryption 
   password (without spaces).

5. Now, run ``signal2html`` on the backup directory, as follows:
   ```
   $ signal2html -i signal_backup/ -o signal_html/
   ```
   This will create a HTML page for each of the message threads in the 
   ``signal_html`` directory, which you can subsequently open in your browser. 

## Notes

This is a hastily-written script that has only been tested on a few Signal 
database versions. I hope it works on other backup versions as well, but if 
you encounter any issues please submit a pull request.

See the LICENSE file for licensing details and copyright.

Please be aware that Signal messages are encrypted for a reason, and your 
contacts may use it specifically because it provides significant privacy. By 
exporting and decrypting your messages, you should take responsibility for 
maintaining this same level of privacy (for instance by only storing the 
plaintext messages on encypted volumes/drives).

Originally written by [Gertjan van den Burg](https://gertjan.dev). See the 
[contributors](https://github.com/GjjvdBurg/signal2html/graphs/contributors) 
file for a full list of all contributors.
