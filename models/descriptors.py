"""
Reusable descriptors for validated attributes.

Descriptors are a more advanced form of encapsulation than a one-off
@property: a single descriptor class implements the get/set protocol once,
and can be reused across multiple attributes and multiple classes simply by
assigning an instance of it as a class attribute.
"""


class ValidatedAttribute:
    """A descriptor that validates a value before storing it on an instance.

    Subclasses implement `validate(value)` and return the (possibly
    normalized) value to store, or raise ValueError if invalid.

    Each instance of this descriptor stores its value in the owning
    instance's __dict__ under a private name derived from the attribute
    name it is assigned to (set automatically via __set_name__).
    """

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        validated = self.validate(value)
        setattr(instance, self.private_name, validated)

    def validate(self, value):
        """Return a normalized value, or raise ValueError if invalid.

        Subclasses must override this method.
        """
        raise NotImplementedError


class NonEmptyString(ValidatedAttribute):
    """A descriptor enforcing that a value is a non-empty, trimmed string."""

    def __init__(self, field_label=None):
        # Human-readable label used in error messages, e.g. "Name" or "Title".
        self.field_label = field_label

    def validate(self, value):
        label = self.field_label or self.public_name.replace("_", " ").title()
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a non-empty string.")
        return value.strip()


class EmailAddress(ValidatedAttribute):
    """A descriptor enforcing a basic email-address format."""

    import re as _re
    _PATTERN = _re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def validate(self, value):
        if not isinstance(value, str) or not self._PATTERN.match(value.strip()):
            raise ValueError(f"Invalid email address: {value!r}")
        return value.strip().lower()


class ChoiceAttribute(ValidatedAttribute):
    """A descriptor restricting a value to a fixed set of allowed choices."""

    def __init__(self, choices, field_label=None):
        self.choices = tuple(choices)
        self.field_label = field_label

    def validate(self, value):
        if value not in self.choices:
            label = self.field_label or self.public_name.replace("_", " ").title()
            raise ValueError(f"Invalid {label.lower()} {value!r}; expected one of {self.choices}.")
        return value


class OptionalDateString(ValidatedAttribute):
    """A descriptor for an optional date stored as a YYYY-MM-DD string."""

    def validate(self, value):
        from datetime import datetime
        if value is None or value == "":
            return None
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except (TypeError, ValueError):
            raise ValueError(f"Invalid date {value!r}; expected format YYYY-MM-DD.")
        return value
