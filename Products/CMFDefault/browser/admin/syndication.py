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
"""Syndication configuration views.
"""

from datetime import datetime

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Int

from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import IFolderish
from Products.CMFDefault.SyndicationTool import SyndicationTool
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.formlib.form import EditFormBase, SettingsEditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.vocabulary import SimpleVocabulary
from Products.CMFDefault.utils import Message as _

available_periods = (
    (u'hourly', 'hourly', _(u'Hourly')),
    (u'daily', 'daily', _(u'Daily')),
    (u'weekly', 'weekly', _(u'Weekly')),
    (u'monthly', 'monthly', _(u'Monthly')),
    (u'yearly', 'yearly', _(u'Yearly')))


class ISyndicationSchema(Interface):

    """Syndication form schema"""

    period = Choice(
        title=_(u"Update period"),
        vocabulary=SimpleVocabulary.fromTitleItems(available_periods),
        default=SyndicationTool.syUpdatePeriod
    )

    frequency = Int(
        title=_(u"Update frequency"),
        description=_(u"This is a multiple of the update period. An"
                      u" update frequency of '3' and an update period"
                      u" of 'Monthly' will mean an update every three months."),
        default=1
    )

    base = Datetime(
        title=_(u"Update base"),
        description=_(u""),
        default=datetime.now()
    )

    max_items = Int(
        title=_(u"Maximum number of items"),
        description=_(u""),
        default=15
    )


class SyndicationToolSchemaAdapter(SchemaAdapterBase):

    """Adapter for ISyndicationTool.
    """

    adapts(IFolderish)
    implements(ISyndicationSchema)

    period  = ProxyFieldProperty(ISyndicationSchema['period'], 'syUpdatePeriod')
    frequency = ProxyFieldProperty(ISyndicationSchema['frequency'], 'syUpdateFrequency')
    base = ProxyFieldProperty(ISyndicationSchema['base'], 'syUpdateBase')
    max_items = ProxyFieldProperty(ISyndicationSchema['max_items'])


class Site(SettingsEditFormBase):

    """Enable or disable syndication for a site."""

    form_fields = form.FormFields(ISyndicationSchema)
    template = ViewPageTemplateFile("syndication.pt")
    allowed = True
    label = _(u"Configure Portal Syndication")

    actions = form.Actions(
        form.Action(
            name="enable",
            label=_(u"Enable Syndication"),
            condition="disabled",
            success="handle_enable",
            ),
        form.Action(
            name="change",
            label=_(u"Change"),
            condition="enabled",
            success="handle_change",
            ),
        form.Action(
            name="disable",
            label=_(u"Disable Syndication"),
            condition="enabled",
            success="handle_disable"
        )
    )

    @property
    @memoize
    def syndtool(self):
        return getUtility(ISyndicationTool)

    @memoize
    def enabled(self, action=None):
        return self.syndtool.isAllowed

    @memoize
    def disabled(self, action=None):
        return not self.syndtool.isAllowed

    def setUpWidgets(self, ignore_request=False):
        fields = self.form_fields
        if self.disabled():
            fields = form.FormFields()
        super(Site, self).setUpWidgets(ignore_request)

    def handle_enable(self, action, data):
        self.syndtool.isAllowed = True
        self.status = _(u"Syndication enabled.")
        self._setRedirect("portal_actions", "global/syndication")

    def handle_change(self, action, data):
        self._handle_success(action, data)
        self.status = _(u"Syndication settings changed.")
        self._setRedirect("portal_actions", "global/syndication")

    def handle_disable(self, action, data):
        self.syndtool.isAllowed = False
        self.status = _(u"Syndication disabled.")
        self._setRedirect("portal_actions", "global/syndication")


# XXX: Don't use this form, it might corrupt your settings!
class Syndicate(SettingsEditFormBase):

    """Enable, disable and customise syndication settings for a folder.
    """

    form_fields = form.FormFields(ISyndicationSchema)
    template = ViewPageTemplateFile("syndication.pt")
    label = _(u"Configure Folder Syndication")

    actions = form.Actions(
        form.Action(
            name="enable",
            label=_(u"Enable Syndication"),
            condition="disabled",
            success="handle_enable",
            ),
        form.Action(
            name="change",
            label=_(u"Change"),
            condition="enabled",
            success="handle_change",
            ),
        form.Action(
            name="revert",
            label=_(u"Revert to Site Default"),
            condition="enabled",
            success="handle_revert",
            ),
        form.Action(
            name="disable",
            label=_(u"Disable Syndication"),
            condition="enabled",
            success="handle_disable",
        )
    )

    @property
    @memoize
    def adapter(self):
        return getAdapter(self.context, ISyndicationInfo)

    def setUpWidgets(self, ignore_request=False):
        fields = self.form_fields
        if self.disabled():
            fields = form.FormFields()
        super(Syndicate, self).setUpWidgets(ignore_request)

    @memoize
    def enabled(self, action=None):
        return self.adapter.enabled

    @memoize
    def disabled(self, action=None):
        return not self.adapter.enabled

    @property
    @memoize
    def allowed(self):
        syndtool = getUtility(ISyndicationTool)
        return syndtool.isSiteSyndicationAllowed()

    def handle_enable(self, action, data):
        self.adapter.enable()
        self.status = _(u"Syndication enabled.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_disable(self, action, data):
        self.adapter.disable()
        self.status = _(u"Syndication disabled.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_change(self, action, data):
        self._handle_success(action, data)
        #self.adapter.set_info(**data)
        self.status = _(u"Syndication settings changed.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_revert(self, action, data):
        self.adapter.revert()
        self.status = _(u"Syndication reset to site default.")
        self._setRedirect("portal_actions", "object/syndication")
