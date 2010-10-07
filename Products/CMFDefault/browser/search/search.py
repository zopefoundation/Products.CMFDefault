##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Search views"""

from zope.interface import Interface
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import memoize

from interfaces import ISearchSchema

class Search(EditFormBase):
    """Portal Search Form"""

    template = ViewPageTemplateFile("search.pt")
    form_fields = form.FormFields(ISearchSchema)

    actions = form.Actions(
        form.Action(
            name='search',
            label=_(u"Search"),
            success='handle_search',
            failure='handle_failure',
            ),
        )

    @property
    def catalog(self):
        return self._getTool('portal_catalog')

    @property
    def types(self):
        return self._getTool('portal_types')

    def handle_search(self, action, data):
        pass
