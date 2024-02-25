from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not isinstance(phone, Phone):
            raise ValueError('Invalid phone value. Use Phone instance')
        self.phones.append(phone)

    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):
            raise ValueError('Invalid birthday value. Use Birthday instance')
        self.birthday = birthday

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = str(self.birthday.value.strftime('%d.%m.%Y')) if self.birthday else 'Not Set'
        return f"Contact name: {self.name}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value.date()

                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:

                    if birthday_this_year.weekday() in [5, 6]:
                        monday_after_birthday = birthday_this_year + timedelta(days=(7 - birthday_this_year.weekday()))
                        congradulation_date = monday_after_birthday.strftime('%d.%m.%Y')
                    else:
                        congradulation_date = birthday_this_year.strftime('%d.%m.%Y')

                    upcoming_birthdays.append({'name': record.name.value, 'congradulation_date': congradulation_date})

        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            error_messages = {
                KeyError: 'Contact not found.',
                ValueError: 'Invalid command format.',
                IndexError: 'Invalid command format.'
            }
            return error_messages.get(type(e), 'An error occured. Please try again.')
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

# Handler function for adding a birthday to a contact
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        print('Usage: add birthday [name] [birthdaydate]')
        return
    name, birthday = args
    try:
        record = book.find(name)
        if record:
            record.add_birthday(Birthday(birthday))
            print(f'Birthday added for {name}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

# Handler function for displaying a contact's birthday
@input_error
def show_birthday(args, book):
    if len(args) != 1:
        print('Usage: show birthday [name]')
        return
    name = args[0]
    try:
        record = book.find(name)
        if record:
            if record.birthday:
                print(f'{name} birthday is on {record.birthday.value.strftime("%d.%m.%Y")}.')
            else:
                print(f'No birthday set for {name}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

# Handler function to display birthdays in the next week
@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print(f'Upcoming birthdays for next week:')
        for contact in upcoming_birthdays:
            print(f"{contact['name']} birthday is on {contact['congradulation_date']}.")
    else:
        print('No upcoming birthdays for next week.')

def main():
    book = AddressBook()
    print('Welcome to the assistant bot!')
    while True:
        user_input = input('Enter a command: ')
        command, *args = user_input.split()

        if command in ['close', 'exit']:
            print('Good bye!')
            break

        elif command == 'hello':
            print('How can I help you?')

        elif command == 'add':
            if len(args) != 2:
                print('Usage: add [name] [phone number]')
                continue
            name, phone = args
            try:
                record = Record(name)
                record.add_phone(Phone(phone))
                book.add_record(record)
                print(f'Contact {name} with phone {phone} added.')
            except ValueError as e:
                print(str(e))
        
        elif command == 'change phone':
            if len(args) != 2:
                print('Usage: change phone [name] [new phone number]')
                continue
            name, new_phone = args
            try:
                record = book.find(name)
                if record:
                    old_phone = str(record.phones[0])
                    record.edit_phone(old_phone, Phone(new_phone))
                    print(f'Phone number for {name} changed from {old_phone} to {new_phone}.')
                else:
                    print(f'Contact {name} not found.')
            except ValueError as e:
                print(str(e))

        elif command == 'phone':
            if len(args) != 1:
                print('Usage: phone [name]')
                continue
            name = args[0]
            try:
                record = book.find(name)
                if record:
                    if record.phones:
                        print(f'Phone number for {name}: {record.phones[0]}')
                    else:
                        print(f'No phone number found for {name}.')
                else:
                    print(f'Contact {name} not found.')
            except ValueError as e:
                print(str(e))

        elif command == 'all':
            if book.data:
                print('All contacts:')
                for name, record in book.data.items():
                    print(record)
            else:
                print('No contacts found.')
        
        elif command == 'add birthday':
            add_birthday(args, book)

        elif command == 'show birthday':
            show_birthday(args, book)

        elif command == 'birthdays':
            birthdays(args, book)

        else:
            print('Invalid command.')

if __name__ == '__main__':
    main()


