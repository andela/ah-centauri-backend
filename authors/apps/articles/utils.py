from rest_framework import serializers
# from collections import OrderedDict

class ChoicesField(serializers.Field):
    """Custom ChoiceField serializer field."""

    def __init__(self, choices, **kwargs):
        """init."""
        self._choices = list(choices)
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        """Used while retrieving value for the field."""
        return obj

    def to_internal_value(self, data):
        """Used while storing value for the field."""
        for i in self._choices:
            if i == data.lower():
                return i
        raise serializers.ValidationError("Acceptable values are {0}.".format(self._choices))