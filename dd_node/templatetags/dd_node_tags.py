# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def display_edit_form():
    """Template tag to disable the edit form in the browsable API.

    This tag can be used to modify the `display_edit_forms`
    context variable in Django REST framework templates.

    """
    return getattr(settings, "DRF_DISPLAY_EDIT_FORM", True)


@register.simple_tag
def display_filter_form():
    """Template tag to disable the filter form in the browsable API.

    This tag can be used to modify the `filter_form`
    context variable in Django REST framework templates.

    """
    return getattr(settings, "DRF_DISPLAY_FILTER_FORM", True)
