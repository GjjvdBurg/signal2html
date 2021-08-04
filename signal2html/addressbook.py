# -*- coding: utf-8 -*-

"""Addressbook functionality

License: See LICENSE file.

"""

import abc
import logging

from .html_colors import get_random_color
from .models import Recipient
from .versioninfo import VersionInfo


class Addressbook(metaclass=abc.ABCMeta):
    """Abstract class that store contacts and groups.

    Note: subclasses must implement at a minimum:

    - `_load_recipients()` to load all recipients
    - `get_recipient_by_address()` to return a specific recipient"""

    def __init__(self, db):
        """Initializes the addressbook and load all known recipients."""
        self.logger = logging.getLogger(__name__)
        self.db = db
        self.rid_to_recipient: dict[str, Recipient] = {}
        self.phone_to_rid: dict[str, str] = {}
        self.uuid_to_rid: dict[str, str] = {}
        self.groups: dict[int, str] = {}

        self._load_groups()
        self._load_recipients()  # Must be implemented by subclass
        self.next_rid = 10000

    @abc.abstractmethod
    def _load_recipients():
        """Load all recipients in the recipient_preferences table."""

    def get_group_title(self, group_id: str) -> str:
        """Retrieves the title of a group given the group_id (long
        hexadecimal-based identifier)."""
        return self.groups.get(group_id)

    @abc.abstractmethod
    def get_recipient_by_address(self, address: str) -> Recipient:
        """Returns a Recipient object that matches the address provided.

        The address is the kind of information found in the address field
        of the mms/sms message tables, but also in recipient_ids of the
        thread table.

        If an address is provided that does not exist in the addressbook,
        it is created on the spot."""

    def get_recipient_by_phone(self, phone: str) -> Recipient:
        """Returns a Recipient object that matches the phone number provided."""
        rid = self.phone_to_rid.get(phone)
        return self.rid_to_recipient.get(rid)

    def get_recipient_by_uuid(self, uuid: str) -> Recipient:
        """Returns a Recipient object that matches the UUID provided."""
        rid = self.uuid_to_rid.get(uuid)
        return self.rid_to_recipient.get(rid)

    def _add_recipient(self, recipient_id, uuid, name, color, isgroup, phone):
        """Adds a recipient to the internal data structures."""
        recipient = Recipient(
            recipient_id,
            name=name,
            color=color,
            isgroup=isgroup,
            phone=phone,
            uuid=uuid,
        )

        self.rid_to_recipient[str(recipient_id)] = recipient
        self.logger.debug(
            f"Adding recipient {str(recipient_id)} and phone {phone}"
        )
        if phone:
            self.phone_to_rid[str(phone)] = str(recipient_id)
        if uuid:
            self.uuid_to_rid[uuid] = str(recipient_id)

        return recipient

    def _get_friendly_name_for_group(self, address: str):
        """Creates a readable group name, either the title or a name derived from the group id."""
        name = self.get_group_title(address)
        if not name:
            gid = self._get_group_id(address)
            if gid:
                return f"Group {gid}"
            else:
                return ""

    def _get_group_id(self, group_id: str) -> str:
        """Gets the integer ID of a group from the Signal database."""
        qry = self.db.execute(
            "SELECT group_id, _id FROM groups WHERE group_id LIKE ?",
            (f"{group_id}",),
        )
        qry_res = qry.fetchone()
        if qry_res:
            return str(qry_res[1])

    def _get_new_rid(self) -> str:
        """Creates a new recipient ID for recipients not in the initial
        addressbook."""
        while self.rid_to_recipient.get(str(self.next_rid)):
            self.next_rid += 1

        return str(self.next_rid)

    def _get_unique_group_id(self, group_id: str) -> str:
        """Given a group ID, returns a unique identifier for the group.

        Group IDs are currently comprised of a type, followed by '!', followed
        by an hexadecimal identifier.

        NOTE: This method currently returns the group id itself, but might be
        used to merge groups that share the same hexadecimal identifier."""
        return group_id

    def _load_groups(self):
        """Loads all group names (a.k.a. titles)."""
        qry = self.db.execute("SELECT group_id, title FROM groups")
        qry_res = qry.fetchall()
        for group_id, title in qry_res:
            self.groups[self._get_unique_group_id(group_id)] = title


class AddressbookV1(Addressbook):
    def get_recipient_by_address(self, address: str) -> Recipient:
        """In this database version, all addresses are directly phone numbers
        or group_id's and creating them might happen if no preferences were
        stored for the particular address."""

        isgroup = self._isgroup(address)
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
                    newrid, "", friendly_name, get_random_color(), True, phone
                )
            else:
                self.logger.info(
                    f"Recipient with phone '{address}' not in addressbook, adding it."
                )
                return self._add_recipient(
                    newrid, "", address, get_random_color(), False, phone
                )
        else:
            return recipient

    def _isgroup(self, address: str) -> bool:
        """Decides whether an address refers to a group."""
        return address.startswith(
            "__textsecure_group__"
        ) or address.startswith("__signal_mms_group__")

    def _load_recipients(self):
        """Load all recipients in the recipient_preferences table.

        In this version of the database, it is normal for recipients in other
        tables not to be found in this table."""
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

            self._add_recipient(recipient_id, "", name, color, isgroup, phone)


class AddressbookV2(Addressbook):
    def get_recipient_by_address(self, address: str) -> Recipient:
        """In this database version, all addresses are recipient_id's and
        creating them here is not expected to happen."""

        rid = str(address)
        recipient = self.rid_to_recipient.get(rid)

        if recipient is None:
            # Create on the spot, but not expected to happen
            self.logger.warn(
                f"Recipient with rid {address} not in addressbook, adding it."
            )
            return self._add_recipient(
                rid, "", "", get_random_color(), False, ""
            )
        else:
            return recipient

    def _isgroup(self, group_id) -> bool:
        """Decides whether a group_id refers to a group."""
        return group_id is not None

    def _load_recipients(self):
        """Load all recipients in the recipient table.

        In this version of the database, all recipients references should be
        found in this table."""
        qry = self.db.execute(
            "SELECT _id, group_id, uuid, "
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
            uuid,
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

            self._add_recipient(
                recipient_id, uuid, name, color, isgroup, phone
            )


def make_addressbook(db, versioninfo) -> Addressbook:
    """Factory function for Addressbook.

    The returned implementation depends on the structure of the Signal database."""
    if versioninfo.is_addressbook_using_rids():
        return AddressbookV2(db)
    return AddressbookV1(db)
