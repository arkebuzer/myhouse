from enum import Enum


class TimePointEnum(Enum):
    MONTH = 'MONTH'
    DAY = 'DAY'
    HOUR = 'HOUR'

    def equals_to_str(self, string):
        """Case insensitive equality test."""
        return self.value == string.upper()

    def __str__(self):
        return self.value
