from functools import wraps
from typing import Dict, Callable, Tuple, Any
from classes import AddressBook, Record


def input_error(func: Callable) -> Callable:
    """Декоратор для обробки типових помилок введення."""

    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as err:
            return str(err)  # "Please provide both name and phone."
        except KeyError as err:
            return f"Contact '{err.args[0]}' not found."
        except IndexError:
            return "Missing arguments."
        except AttributeError as err:
            return str(err)

    return inner


@input_error
def parse_input(user_input: str) -> Tuple[str, ...]:
    """
    Розбирає рядок введення на команду та аргументи.
    Повертає кортеж: (command, *args)
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args: list[str], contacts: AddressBook) -> str:
    """Додає новий контакт або телефон до існуючого."""
    name, phone = args
    record = contacts.find(name)

    if record:
        record.add_phone(phone)
        return "Contact update"
    else:
        record = Record(name)
        record.add_phone(str(phone))
        contacts.add_record(record)
        return "Contact added."


@input_error
def change_contact(args: list[str], contacts: AddressBook) -> str:
    """Змінює існуючий номер телефону."""
    name, old_phone, new_phone = args
    record = contacts.find(name)

    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "The contact is not in the phonebook."


@input_error
def show_phone(args: list[str], contacts: AddressBook) -> str:
    """Показує повну інформацію про контакт."""
    name = args[0]
    record = contacts.find(name)

    if record:
        return record
    else:
        return "Contact not found"


@input_error
def birthday(args: list[str], contacts: AddressBook) -> list[str] | str:
    """
    Повертає список дат найближчих днів народження
    (наступні 7 днів).
    """
    birthday_days = contacts.get_upcoming_birthdays()

    return birthday_days


@input_error
def add_birthday(args: list[str], contacts: AddressBook) -> str:
    """Додає або оновлює день народження контакту."""
    name, date = args
    record = contacts.find(name)

    record.add_birthday(date)
    return "Birthday updated."


@input_error
def show_birthday(args: list[str], contacts: AddressBook) -> str:
    """Показує день народження контакту."""
    name = args[0]
    record = contacts.find(name)

    return record.find_birthday


@input_error
def show_all(args: list[str], contacts: AddressBook) -> str:
    """Повертає всі записи телефонної книги."""
    return contacts


def main() -> None:
    """Точка входу програми."""
    book = AddressBook()

    COMMANDS: Dict[str, Callable[[list[str], AddressBook], Any]] = {
        'add': add_contact,
        'change': change_contact,
        'phone': show_phone,
        'all': show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthday
    }

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")

        if not user_input:
            print("Please enter a command.")
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command in COMMANDS:
            print(COMMANDS[command](args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
