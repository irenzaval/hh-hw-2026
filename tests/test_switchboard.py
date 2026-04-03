import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_create_user_local() -> None:
    user = Switchboard.create_user("1", "Ivan Ivanov", "+79990000000")
    assert isinstance(user, LocalUser)
    assert user.id == 1
    assert user.fullname == "Ivan Ivanov"
    assert user.phone == "+79990000000"


def test_create_user_foreign() -> None:
    user = Switchboard.create_user("2", "John Smith", "+44123456789")
    assert isinstance(user, ForeignUser)
    assert user.id == 2
    assert user.fullname == "John Smith"
    assert user.phone == "+44123456789"


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_register_call_with_local_both_sides() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert not active_call.is_cross_border


def test_register_call_with_foreign_both_sides() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,John Smith,+44123456789,2,Jane Doe,+44234567890"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert not active_call.is_cross_border


def test_register_call_with_spaces_in_raw_call() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        " 1 , Ivan Ivanov , +79990000000 , 2 , John Smith , +15551234567 "
    )

    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_without_plus_in_phone_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Incorrect format of phone number"):
        switchboard.register_call("1,Ivan,+79990000000,2,John,44123456789")


def test_register_call_with_letters_in_phone_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Incorrect format of phone number"):
        switchboard.register_call("1,Ivan,+7999abc0000,2,John,+44123456789")


def test_register_call_with_wrong_amount_of_fields_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Invalid call format. Expected 6 fields, got 5"):
        switchboard.register_call("1,Ivan,+79990000000,2,John")


def test_register_call_with_empty_raw_call_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Information about call cannot be empty"):
        switchboard.register_call(" ")


def test_register_call_with_invalid_user_id_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call("abc,Ivan,+79990000000,2,John,+15551234567")


def test_register_call_should_not_increment_counter_on_error() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call("invalid data")

    assert switchboard.get_active_calls_count() == 0


def test_register_call_with_only_plus_in_phone_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Incorrect format of phone number"):
        switchboard.register_call("1,Ivan,+,2,John,+15551234567")


def test_register_call_with_numbers_in_name_should_raise_exception() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Incorrect format of fullname"):
        switchboard.register_call("1,Ivan111,+79990000000,2,John,+15551234567")
