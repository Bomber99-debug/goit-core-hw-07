from collections import UserDict
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Field:
    """Базовий клас для полів контакту."""
    value: str

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Поле імені контакту."""
    pass


@dataclass
class Phone(Field):
    """Поле телефону з валідацією (рівно 10 цифр)."""

    def __post_init__(self) -> None:
        if len(self.value) != 10 or not self.value.isdigit():
            raise ValueError(f"Phone number '{self.value}' is not valid")


@dataclass()
class Birthday(Field):
    """Поле дня народження у форматі DD.MM.YYYY."""

    def __post_init__(self) -> None:
        try:
            datetime.strptime(self.value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    """Окремий контакт: ім'я, телефони, день народження."""

    def __init__(self, name: str):
        self.name: Name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, value: str) -> None:
        """Додає телефон до списку, якщо такого номера ще немає."""
        if self.find_phone(value) is None:
            self.phones.append(Phone(value))
        else:
            raise ValueError("Phone number already exists.")

    def remove_phone(self, value: str | Phone) -> None:
        """Видаляє телефон (за рядком або об'єктом Phone)."""
        if isinstance(value, str):
            value = self.find_phone(value)

        if value:
            self.phones.remove(value)

    def edit_phone(self, value: str, replace: str) -> None:
        """Замінює існуючий телефон на новий."""
        phone_obj = self.find_phone(value)

        if phone_obj:
            # Спочатку додаємо новий номер, потім видаляємо старий
            self.add_phone(replace)
            self.remove_phone(phone_obj)
        else:
            raise ValueError(
                f"The phone number '{value}' is not in the contact's phone list"
            )

    def find_phone(self, value: str) -> Optional[Phone]:
        """Повертає об'єкт Phone за номером або None, якщо номер не знайдено."""
        return next((i for i in self.phones if i.value == value), None)

    def add_birthday(self, date: str) -> None:
        """Додає день народження контакту."""
        self.birthday = Birthday(date)

    @property
    def phones_as_string(self) -> str:
        """Повертає всі телефони контакту одним рядком через кому."""
        return ', '.join(i.value for i in self.phones)

    @property
    def find_birthday(self) -> str:
        """Повертає дату народження або викликає помилку, якщо її немає."""
        if self.birthday:
            return self.birthday.value
        else:
            raise AttributeError("Birthday is not set for this contact")

    def __str__(self) -> str:
        """Рядкове представлення контакту."""
        return (
            f"Contact name: {self.name.value}, "
            f"Birthday: {self.birthday}, "
            f"phones: {', '.join(i.value for i in self.phones)}"
        )


class AddressBook(UserDict):
    """Колекція контактів (ключ — ім'я, значення — Record)."""

    def add_record(self, value: Record) -> None:
        """Додає Record до телефонної книги."""
        self.data[value.name.value] = value

    def find(self, value: str) -> Record:
        """Повертає контакт за ім'ям або викликає KeyError, якщо не знайдено."""
        return self.data[value]

    def delete(self, value: str) -> None:
        """Видаляє контакт за ім'ям."""
        if value in self.data:
            del self.data[value]
        else:
            raise ValueError(f"Name '{value}' is not found in AddressBook")

    def get_upcoming_birthdays(self) -> List[str]:
        """
        Повертає список дат днів народження,
        що припадають на наступні 7 днів.
        """

        def find_next_weekday(start_date: datetime.date, weekday: int):
            """Переносить дату на найближчий вказаний будній день."""
            return start_date + timedelta(
                (weekday - start_date.weekday()) % 7 or 7
            )

        def adjust_for_weekend(birthday):
            """Якщо дата припадає на вихідний, переносить її на понеділок."""
            weekday = birthday.weekday()
            if weekday >= 5:
                birthday = find_next_weekday(birthday, 0)
            return birthday

        upcoming_birthdays: List[str] = []
        today = datetime.today().date()

        for k in self.data.values():
            try:
                birthday_date = datetime.strptime(
                    k.find_birthday, "%d.%m.%Y"
                ).date()
            except:
                # Якщо день народження не вказаний або невалідний, контакт пропускаємо
                continue

            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year > today:
                birthday_day = (birthday_this_year - today).days

                if birthday_day <= 7:
                    birthday_this_year = adjust_for_weekend(
                        birthday_this_year
                    )
                    upcoming_birthdays.append(str(birthday_this_year))

        if upcoming_birthdays:
            return upcoming_birthdays
        else:
            raise AttributeError("No birthdays found")

    def __str__(self) -> str:
        """Повертає всі контакти як багаторядковий рядок."""
        return '\n'.join(str(v) for v in self.data.values())
