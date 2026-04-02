from __future__ import annotations

from dataclasses import dataclass

from app.users import User
from app.users.local_user import LocalUser
from app.users.foreign_user import ForeignUser

FIELDS_COUNT = 6
PHONE_PREFIX = "+"
LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


class Switchboard:
    def __init__(self) -> None:
        self._active_calls_count: int = 0
        self._cross_border_calls_count: int = 0
        self._active_calls: list[ActiveCall] = []

    @staticmethod
    def create_user(user_id: str, fullname: str, phone: str) -> User:
        user_id_int = Switchboard._parse_user_id(user_id)

        if phone.startswith(LOCAL_PHONE_PREFIX):
            return LocalUser(user_id_int, fullname, phone)
        else:
            return ForeignUser(user_id_int, fullname, phone)
        
    @staticmethod
    def _validate_phone(phone: str) -> None:
        if not phone.startswith(PHONE_PREFIX) or not phone[1:].isdigit():
            raise ValueError("Incorrect format of phone number")

    @staticmethod
    def _validate_name(name: str) -> None:
        if not all(char.isalpha() or char in {" ", "-"} for char in name ):
            raise ValueError("Incorrect format of fullname")

    @staticmethod
    def _parse_user_id(user_id: str) -> int:
        if not user_id.isdigit():
            raise ValueError("User id must be numeric")
        return int(user_id)

    def register_call(self, raw_call: str) -> ActiveCall:
        if not raw_call or not raw_call.strip():
            raise ValueError("Information about call cannot be empty")

        call_information = [field.strip() for field in raw_call.split(',')]

        if len(call_information) != FIELDS_COUNT:
            raise ValueError(f"Invalid call format. Expected 6 fields, got {len(call_information)}")

        caller_id, caller_name, caller_phone, receiver_id, receiver_name, receiver_phone = call_information

        self._validate_phone(caller_phone)
        self._validate_phone(receiver_phone)

        self._validate_name(caller_name)
        self._validate_name(receiver_name)

        caller = self.create_user(caller_id, caller_name, caller_phone)
        receiver = self.create_user(receiver_id, receiver_name, receiver_phone)

        active_call = ActiveCall(caller=caller, receiver=receiver)

        self._active_calls.append(active_call)

        self._active_calls_count += 1

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        return active_call

    def get_active_calls_count(self) -> int:
        return self._active_calls_count

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count
