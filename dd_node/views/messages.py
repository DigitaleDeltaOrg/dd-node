# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from stored_messages.views import InboxViewSet as InboxViewSetBase


class InboxViewSet(InboxViewSetBase):

    # Override the default permission class, i.e. OrganisationRolePermission.
    # POST is allowed by any authenticated user, not just admins.
    @detail_route(methods=['POST'], permission_classes=[IsAuthenticated])
    def read(self, request, pk=None):
        return super(InboxViewSet, self).read(request, pk)
