"""
Shared base classes providing identity, comparison, and serialization
behavior to every model in ProjectFlow.

This module demonstrates several "advanced" OOP techniques:

- Identifiable is an abstract base class (ABC) that every entity inherits
  from. Each subclass automatically gets its OWN independent ID counter via
  __init_subclass__, so User, Project, and Task never collide on IDs without
  any subclass needing to redeclare counter logic.
- Identifiable also implements __eq__, __hash__, and __lt__ so entities of
  the same type can be compared and sorted by ID out of the box.
- Serializable is a mixin defining the to_dict/from_dict contract as
  abstract methods, plus a polymorphic `summary()` template method that
  calls an abstract `_summary_fields()` hook implemented differently by
  each concrete subclass (User, Project, Task) — classic dynamic dispatch.
"""

from abc import ABC, abstractmethod


class Identifiable(ABC):
    """Abstract base providing auto-incrementing, per-subclass IDs.

    Any class that inherits from Identifiable automatically receives its
    own `_id_counter` class attribute, independent of any other subclass.
    This is set up dynamically in __init_subclass__ so individual model
    classes don't need to declare `_next_id = 1` themselves.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Give every concrete subclass its own counter, starting at 1.
        cls._id_counter = 1

    def __init__(self, entity_id=None):
        cls = type(self)
        if entity_id is None:
            entity_id = cls._id_counter
            cls._id_counter += 1
        else:
            cls._id_counter = max(cls._id_counter, entity_id + 1)
        self._id = entity_id

    @property
    def id(self):
        """Return this entity's unique ID (read-only, scoped to its class)."""
        return self._id

    def __eq__(self, other):
        if not isinstance(other, Identifiable):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self):
        return hash((type(self).__name__, self.id))

    def __lt__(self, other):
        if not isinstance(other, Identifiable) or type(self) is not type(other):
            return NotImplemented
        return self.id < other.id


class Serializable(ABC):
    """Mixin defining the serialization contract and a polymorphic summary.

    Concrete subclasses must implement `to_dict()`, `from_dict()`, and
    `_summary_fields()`. `summary()` is a template method: it is identical
    for every entity type but produces type-specific output because it
    delegates the field list to `_summary_fields()`, which each subclass
    overrides.
    """

    @abstractmethod
    def to_dict(self):
        """Serialize this object to a JSON-friendly dict."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Reconstruct an instance of this class from a dict."""
        raise NotImplementedError

    @abstractmethod
    def _summary_fields(self):
        """Return a list of (label, value) pairs describing this entity.

        Subclasses override this to control what appears in summary().
        """
        raise NotImplementedError

    def summary(self):
        """Return a one-line, human-readable summary of this entity.

        This method is identical across all entity types but produces
        different output for each, because it relies on the
        type-specific `_summary_fields()` implementation -- a simple
        example of polymorphism / dynamic dispatch.
        """
        kind = type(self).__name__
        fields = ", ".join(f"{label}: {value}" for label, value in self._summary_fields())
        return f"{kind} #{self.id} — {fields}"
