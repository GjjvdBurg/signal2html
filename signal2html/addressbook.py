"""Addressbook functionality

License: See LICENSE file.

"""

import logging
import sqlite3

from enum import Enum

from .html_colors import get_random_color
from .models import Recipient


class Addressbook(object):
    def __init__(self, db, version):
        self.logger = logging.getLogger(__name__)
        self.db = db
        self.version = int(version)
        self.rid_to_recipient: dict[str, Recipient] = {}
        self.phone_to_rid: dict[str, str] = {}
        self.groups: dict[int, str] = {}

        self._load_groups()
        self._load_recipients()
        self.next_rid = 10000

    def _add_recipient(self, recipient_id, name, color, isgroup, phone):
        recipient = Recipient(
            recipient_id, name=name, color=color, isgroup=isgroup, phone=phone
        )

        self.rid_to_recipient[str(recipient_id)] = recipient
        self.logger.debug(
            f"Adding recipient {str(recipient_id)} and phone {phone}"
        )
        if phone:
            self.phone_to_rid[str(phone)] = str(recipient_id)

        return recipient

    def _get_friendly_name_for_group(self, address: str):
        name = self.get_group_title(address)
        if not name:
            gid = self._get_group_id(address)
            if gid:
                return f"Group {gid}"
            else:
                return ""

    def _get_group_id(self, group_id: str) -> str:
        qry = self.db.execute(
            "SELECT group_id, _id FROM groups WHERE group_id LIKE ?",
            (f"{group_id}",),
        )
        qry_res = qry.fetchone()
        if qry_res:
            return str(qry_res[1])

    def _get_new_rid(self) -> str:
        while self.rid_to_recipient.get(str(self.next_rid)):
            self.next_rid += 1

        return str(self.next_rid)

    def _get_unique_group_id(self, group_id: str) -> str:
        return group_id

    def _load_groups(self):
        qry = self.db.execute("SELECT group_id, title FROM groups")
        qry_res = qry.fetchall()
        for group_id, title in qry_res:
            self.groups[self._get_unique_group_id(group_id)] = title

    def get_group_title(self, group_id: str) -> str:
        return self.groups.get(group_id)

    def get_recipient_by_phone(self, phone: str) -> Recipient:
        rid = self.phone_to_rid.get(phone)
        return self.rid_to_recipient.get(rid)


class AddressbookV1(Addressbook):
    def _isgroup(self, address: str) -> bool:
        return address.startswith(
            "__textsecure_group__"
        ) or address.startswith("__signal_mms_group__")

    def _load_recipients(self):
        qry = self.db.execute(
            "SELECT _id, recipient_ids, system_display_name, color, signal_profile_name "
            "FROM recipient_preferences "
        )
        qry_res = qry.fetchall()

        for (
            recipient_id,
            phone,
            system_display_name,
            color,
            profile_name,
        ) in qry_res:
            isgroup = self._isgroup(phone)
            if isgroup:
                phone = self._get_unique_group_id(phone)
                name = self.get_group_title(phone)
                if name is None:
                    name = self._get_friendly_name_for_group(phone)
                    self.logger.warn(
                        f"Group for recipient {recipient_id} will be named '{name}'."
                    )
            else:
                name = system_display_name or profile_name or phone or ""

            if color is None:
                color = get_random_color()

            self._add_recipient(recipient_id, name, color, isgroup, phone)

    def get_recipient_by_address(self, address: str) -> Recipient:
        isgroup = self._isgroup(address)
        # For V1, address is a phone (or groupid)
        if isgroup:
            phone = self._get_unique_group_id(address)
        else:
            phone = address

        rid = self.phone_to_rid.get(phone)
        recipient = self.rid_to_recipient.get(rid)

        if recipient is None:
            # Create on the spot
            newrid = self._get_new_rid()
            if isgroup:
                friendly_name = self._get_friendly_name_for_group(phone)
                if friendly_name:
                    self.logger.info(
                        f"Group '{phone}' not in addressbook, adding it as '{friendly_name}'."
                    )
                else:
                    self.logger.warn(
                        f"Group '{phone}' not in addressbook, adding it with new ID {newrid}."
                    )
                return self._add_recipient(
                    newrid, friendly_name, get_random_color(), True, phone
                )
            else:
                self.logger.info(
                    f"Recipient with phone '{address}' not in addressbook, adding it."
                )
                return self._add_recipient(
                    newrid, address, get_random_color(), False, phone
                )
        else:
            return recipient


class AddressbookV2(Addressbook):
    def _isgroup(self, group_id) -> bool:
        return group_id is not None

    def _load_recipients(self):
        qry = self.db.execute(
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
            system_display_name,
            profile_joined_name,
            color,
        ) in qry_res:
            isgroup = self._isgroup(group_id)
            if isgroup:
                name = self.get_group_title(group_id)
                if name is None:
                    name = self._get_friendly_name_for_group(group_id)
                    if name:
                        self.logger.info(
                            f"Group for recipient {recipient_id} is '{group_id}' and will be called by group id using name '{name}'."
                        )
                    else:
                        self.logger.warn(
                            f"Group for recipient {recipient_id} is '{group_id}' which does not exist."
                        )
            else:
                name = (
                    system_display_name or profile_joined_name or phone or ""
                )

            if color is None:
                color = get_random_color()

            self._add_recipient(recipient_id, name, color, isgroup, phone)

    def get_recipient_by_address(self, address: str) -> Recipient:
        # For V2, address is a recipient_id
        rid = address
        recipient = self.rid_to_recipient.get(rid)

        if recipient is None:
            # Create on the spot, but not expected to happen
            self.logger.warn(
                f"Recipient with rid {address} not in addressbook, adding it."
            )
            return self._add_recipient(rid, "", get_random_color(), False, "")
        else:
            return recipient


def make_addressbook(db, version):
    """Factory function for Addressbook"""
    if int(version) <= 23:
        return AddressbookV1(db, version)
    else:
        return AddressbookV2(db, version)
