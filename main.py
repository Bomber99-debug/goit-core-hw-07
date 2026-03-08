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
            return str(err)  # Повертаємо текст помилки валідації користувачу
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


def validate_args(args: list[str], nums: int) -> list[str]:
    """Перевіряє точну кількість аргументів для команди."""
    if len(args) == nums:
        return args
    else:
        raise ValueError("Invalid number of arguments.")


@input_error
def add_contact(args: list[str], contacts: AddressBook) -> str:
    """Додає новий контакт або телефон до існуючого."""
    name, phone = validate_args(args, 2)

    try:
        # Якщо контакт уже існує, пробуємо додати ще один номер
        record = contacts.find(name)
        record.add_phone(phone)
        return "Contact updated."
    except KeyError:
        # Якщо контакту ще немає, створюємо новий запис
        record = Record(name)
        record.add_phone(phone)
        contacts.add_record(record)
        return "Contact added."


@input_error
def change_contact(args: list[str], contacts: AddressBook) -> str:
    """Змінює існуючий номер телефону."""
    name, old_phone, new_phone = validate_args(args, 3)
    record = contacts.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list[str], contacts: AddressBook) -> str:
    """Показує тільки телефони контакту."""
    name = args[0]
    record = contacts.find(name)
    return record.phones_as_string


@input_error
def birthday(_: list[str], contacts: AddressBook) -> list[str] | str:
    """
    Повертає список дат найближчих днів народження
    (наступні 7 днів).
    """
    birthday_days = contacts.get_upcoming_birthdays()
    return birthday_days


@input_error
def add_birthday(args: list[str], contacts: AddressBook) -> str:
    """Додає або оновлює день народження контакту."""
    name, date = validate_args(args, 2)
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
def show_all(_: list[str], contacts: AddressBook) -> str:
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