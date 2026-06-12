from models.descriptors import NonEmptyString, EmailAddress


class Person:
    """
    Base class representing a person with a name and an email address.

    This class is intended to be subclassed (e.g. by User). It demonstrates
    encapsulation via descriptors: `name` and `email` are validated through
    reusable ValidatedAttribute descriptors rather than one-off properties.
    """

    name = NonEmptyString(field_label="Name")
    email = EmailAddress()

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __str__(self):
        return f"{self.name} <{self.email}>"
