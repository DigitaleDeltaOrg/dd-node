# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import unicode_literals

import logging
import sys
import traceback

from django.conf import settings
from rest_framework.exceptions import APIException as BaseException

logger = logging.getLogger(__name__)

EXCEPTION_MAP = {
    #                          HTTP CODE  DESCRIPTION
    #                          ==== ===== ===========
    # Functional problems
    'ParseError':              (400,  10, "Incorrect request format."),
    'InvalidKey':              (400,  11, "Invalid key in request."),
    'ValidationError':         (400,  20, "Incomplete request content."),
    'UnsupportedMediaType':    (400,  21, "Unsupported media type."),
    'NotAuthenticated':        (401,  10, "Not authenticated"),
    'AuthenticationFailed':    (401,  20, "Authentication failed."),
    'AutheticationFailed':     (401,  21, "Authentication failed."),
    'PermissionDenied':        (403,  10, "Permission denied."),
    'Http404':                 (404,  10, "Resource not found."),
    'DoesNotExist':            (404,  11, "Resource not found."),
    'MultipleObjectsReturned': (404,  12, "Resource not found."),
    'MethodNotAllowed':        (405,  10, "Request method not available."),
    'NotAcceptable':           (406,  10, "Could not satisfy Accept header."),
    'EnhanceYourCalm':         (420,  10, "Aborted."),
    # Technical problems
    'Exception':               (500,   0, "Unknown technical error."),
    'UnknownUnknown':          (500,   1, "Unknown technical error."),
    'KnownUnknown':            (500,   2, "Unknown technical error."),
    'NameError':               (500,  10, "Technical error"),
    'TypeError':               (500,  11, "Technical error."),
    'UnboundLocalError':       (500,  12, "Technical error."),
    'AttributeError':          (500,  13, "Technical error."),
    'RuntimeError':            (500,  14, "Technical error."),
    'ValueError':              (500,  15, "Incorrect parameter value format."),
    'IndexError':              (500,  16, "Technical error."),
    'DatabaseError':           (500,  20, "Database error."),
    'FieldError':              (500,  21, "Database error."),
    'IOError':                 (500,  30, "Disk error."),
    'AllServersUnavailable':   (502,  10, "External server unavailable."),
    'TTransportException':     (502,  11, "External server unavailable."),
    'MaximumRetryException':   (502,  20, "External server error."),
}


class APIException(BaseException):
    """
    This exception wraps another exception (the one that actually occurred).
    Django Rest Framework will catch this exception and render it with the
    appropriate renderer. If DRF is not used, the exception can be used as
    string.
    """
    status_code = None
    code = None
    message = None
    exception = None
    trace = []

    def __init__(self, ex):
        self.exception = ex
        ex_name = ex.__class__.__name__
        if ex_name not in EXCEPTION_MAP:
            ex_name = 'Exception'
        self.status_code, self.code, self.message = EXCEPTION_MAP[ex_name]
        if ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.trace = traceback.extract_tb(exc_traceback)
            if len(self.trace) > 0:
                file, line, method, expr = self.trace[-1]
            else:
                file, line = "", 0
            msg = '{}: {} in {}, line {}'.format(
                ex.__class__.__name__,
                ', '.join(str(x) for x in ex.args),
                file,
                line
            )
            if self.status_code < 500:
                logger.debug('%s - %s', self.detail, msg)
            else:
                logger.exception(self.detail)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.detail

    @property
    def detail(self):
        args = ', '.join(
            str(x) for x in self.exception.args if x is not None
        )
        serialized = {
            'status': self.status_code,
            'code': self.code,
            'message': '{} #{}.{}'.format(
                self.message, self.status_code, self.code),
            'detail': getattr(self.exception, 'detail', args),
        }
        if getattr(settings, "DEBUG", False):
            serialized['exception'] = self.exception.__class__.__name__
            serialized['trace'] = [
                '{}, line {}, in {}: {}'.format(file, line, method, expr)
                for (file, line, method, expr) in self.trace
            ]
        return serialized


class MissingDataException(Exception):
    """Used by the 3Di import to signify that something is missing."""
    pass


class EnhanceYourCalm(Exception):
    pass
