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
import datetime

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.widgets import ChoiceMultiSelectWidget
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.content.interfaces import IBatchForm
from Products.CMFDefault.browser.content.folder import BatchViewBase

from interfaces import ISearchSchema

EPOCH = datetime.date(1970, 1, 1)


class Search(BatchViewBase, EditFormBase):
    """Portal Search Form"""

    template = ViewPageTemplateFile("search.pt")
    results = ViewPageTemplateFile("results.pt")
    hidden_fields = form.FormFields(IBatchForm)
    form_fields = form.FormFields(ISearchSchema)
    form_fields['review_state'].custom_widget = ChoiceMultiSelectWidget
    form_fields['Subject'].custom_widget = ChoiceMultiSelectWidget
    form_fields['portal_type'].custom_widget = ChoiceMultiSelectWidget
    prefix = 'form'

    actions = form.Actions(
        form.Action(
            name='search',
            label=_(u"Search"),
            success='handle_search',
            failure='handle_failure',
            ),
        )

    #def __init__(self, *args):
        #super(Search, self).__init__(*args)
        #self.hidden_fields += self.form_fields

    @property
    def catalog(self):
        return self._getTool('portal_catalog')

    @property
    def types(self):
        return self._getTool('portal_types')

    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the folder contents."""
        super(Search, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(
                self.form_fields, self.prefix, self.context,
                self.request, ignore_request=ignore_request)

    def handle_search(self, action, data):
        for k, v in data.items():
            if k in ('review_state', 'Title', 'Subject', 'Description',
                     'portal_type', 'listCreators'):
                if type(v) == type([]):
                    v = filter(None, v)
                if not v:
                    del data[k]
            elif k == 'created' and v == EPOCH:
                del data[k]

        self._items = self.catalog.searchResults(data)
        self.template = self.results

    def _get_items(self):
        return getattr(self, '_items', ())

    def listBatchItems(self):
        return( {'description': item.Description,
           'icon': item.getIconURL,
           'title': item.Title,
           'type': item.Type,
           'date': item.Date,
           'url': item.getURL(),
           'format': None}
          for item in self._getBatchObj())
