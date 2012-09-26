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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.formlib import form

from .interfaces import ISearchSchema
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.widgets.batch import BatchFormMixin
from Products.CMFDefault.browser.widgets.batch import IBatchForm
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.widgets import ChoiceMultiSelectWidget
from Products.CMFDefault.utils import Message as _

EPOCH = datetime.date(1970, 1, 1)


class Search(BatchFormMixin, EditFormBase):

    """Portal Search Form"""

    template = ViewPageTemplateFile("search.pt")
    results = ViewPageTemplateFile("search_results.pt")
    hidden_fields = form.FormFields(IBatchForm)
    form_fields = form.FormFields(ISearchSchema)
    form_fields['review_state'].custom_widget = ChoiceMultiSelectWidget
    form_fields['Subject'].custom_widget = ChoiceMultiSelectWidget
    form_fields['portal_type'].custom_widget = ChoiceMultiSelectWidget

    search = form.Actions(
        form.Action(
            name='search',
            label=_(u"Search"),
            success='handle_search',
            failure='handle_failure',
            ),
        )

    # for handling searches from the search box
    image = form.Actions(
        form.Action(
            name='search.x',
            label=_(u"Search"),
            success='handle_search',
            failure='handle_failure',
            ),
        form.Action(
            name='search.y',
            label=_(u"Search"),
            success='handle_search',
            failure='handle_failure',
            ),
        )

    actions = search + image

    @property
    @memoize
    def catalog(self):
        return getUtility(ICatalogTool)

    @property
    @memoize
    def is_anonymous(self):
        mtool = getUtility(IMembershipTool)
        return mtool.isAnonymousUser()

    @memoize
    def _getNavigationVars(self):
        data = {}
        if hasattr(self, 'hidden_widgets'):
            form.getWidgetsData(self.hidden_widgets, self.prefix, data)
        if hasattr(self, '_query'):
            data.update(self._query)
        else:
            data = self.request.form
        return data

    @property
    @memoize
    def search_fields(self):
        if self.is_anonymous:
            return self.form_fields.omit('review_state')
        else:
            return self.form_fields

    def setUpWidgets(self, ignore_request=False):
        if "form.b_start" in self.request.form \
        or "b_start" in self.request.form:
            self.template = self.results
        super(Search, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(
                self.search_fields, self.prefix, self.context,
                self.request, ignore_request=ignore_request)

    def handle_search(self, action, data):
        for k, v in data.items():
            if k in ('review_state', 'Title', 'Subject', 'Description',
                     'portal_type', 'listCreators', 'SearchableText'):
                if not v or v == u"None":
                    del data[k]
            elif k == 'created' and v == EPOCH:
                del data[k]
        self._query = data
        self.template = self.results

    @memoize
    def _get_items(self):
        return self.catalog.searchResults(self._query)

    @memoize
    def listBatchItems(self):
        return({'description': item.Description,
           'icon': item.getIconURL,
           'title': item.Title,
           'type': item.Type,
           'date': item.Date,
           'url': item.getURL(),
           'format': None}
          for item in self._getBatchObj())
