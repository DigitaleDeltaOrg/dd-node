# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import unicode_literals

from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from dd_node.utils.conversion import datetime_to_milliseconds as ms


class DisplayValueChoiceField(serializers.ChoiceField):
    default_error_messages = {
        'unknown_choice': 'unknown choice {data}',
    }

    def to_representation(self, value):
        try:
            return dict(self.choices)[value]
        # Django only accepts "an iterable (e.g., a list or tuple) consisting
        # itself of iterables of exactly two items" as choices, so we can
        # always safely cast it to a dictionary and don't need to catch a
        # ValueError.
        except KeyError:
            return 'unknown choice (%s)' % str(value)

    def to_internal_value(self, data):
        """ Will check the input against both the keys and the values of the
        choices.
        """
        choices = dict(self.choices)

        # Check if the input matches with a key in the choices dict
        choices_key_type = type(choices.keys()[0])
        try:
            check_key = choices_key_type(data)
        except ValueError:
            pass
        else:
            if check_key in choices.keys():
                return check_key

        # Check if the input matches with a value in the choices dict
        # Assuming no duplicate values:
        swapped_key_value_choices = dict(
            zip(choices.values(),
                choices.keys())
        )
        try:
            return swapped_key_value_choices[data]
        except (ValueError, KeyError):
            self.fail('unknown_choice', data=str(data))


class LastValue(serializers.HyperlinkedIdentityField):
    def get_attribute(self, obj):
        # Pass the entire object through to `to_representation()`,
        # instead of the standard attribute lookup.
        return obj

    def to_representation(self, value):
        # The value is passed down from the `get_attribute` method
        # and therefore contains the entire object.
        if value.is_file:
            last = value.end
            if last:
                return reverse(
                    'timeseries-data-detail',
                    args=[value.uuid, int(ms(last))],
                    request=self.context['request']
                )
            return None
        return value.last_value


class TimestampField(serializers.Field):
    def to_internal_value(self, data):
        """Convert milliseconds since epoch to datetime.

        NOTE: what to do with timezones?

        Args:
            * data (integer): milliseconds since epoch

        Returns:
            * python datetime object
        """
        return datetime.fromtimestamp(int(data) / 1000)

    def to_representation(self, value):
        "Convert datetime to milliseconds since epoch."
        if isinstance(value, datetime):
            return int(ms(value))
        return value


class JSONSerializerField(serializers.Field):
    def __init__(self, **kwargs):
        super(JSONSerializerField, self).__init__(**kwargs)
        self.style = {'base_template': 'textarea.html'}

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class UUIDField(serializers.UUIDField):
    """A UUIDField that strips leading and trailing whitespace.

    Django REST framework's CharField and its subclasses trim whitespace by
    default (trim_whitespace=True). This is not the case for UUIDField,
    which inherits from Field.

    Solves https://github.com/nens/lizard-nxt/issues/1375.

    """
    def to_internal_value(self, data):
        return super(UUIDField, self).to_internal_value(data.strip())
