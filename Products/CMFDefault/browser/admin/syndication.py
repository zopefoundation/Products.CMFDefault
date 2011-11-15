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
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import adapts
from zope.interface import alsoProvides
from zope.formlib import form
from zope.interface import implements

from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import IFolderish
from Products.CMFDefault.SyndicationTool import SyndicationTool
from Products.CMFDefault.SyndicationInfo import ISyndicationInfo
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.formlib.form import SettingsEditFormBase, EditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.utils import Message as _


class Site(SettingsEditFormBase):

    """Enable or disable syndication for a site."""

    form_fields = form.FormFields(ISyndicationInfo)
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

    @memoize
    def enabled(self, action=None):
        return self.getContent().enabled

    @memoize
    def disabled(self, action=None):
        return not self.getContent().enabled

    @memoize
    def getContent(self):
        syndtool = getUtility(ISyndicationTool)
        return syndtool

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        super(Site, self).setUpWidgets(ignore_request)
        self.widgets['enabled'].hide = True

    def handle_enable(self, action, data):
        self.getContent().enabled = True
        self._handle_success(action, data)
        self.status = _(u"Syndication enabled.")
        self._setRedirect("portal_actions", "global/syndication")

    def handle_change(self, action, data):
        self._handle_success(action, data)
        self.status = _(u"Syndication settings changed.")
        self._setRedirect("portal_actions", "global/syndication")

    def handle_disable(self, action, data):
        self.getContent().enabled = False
        self.status = _(u"Syndication disabled.")
        self._setRedirect("portal_actions", "global/syndication")


class Folder(SettingsEditFormBase):

    """Enable, disable and customise syndication settings for a folder.
    """

    form_fields = form.FormFields(ISyndicationInfo)
    label = _(u"Configure Folder Syndication")

    actions = form.Actions(
        form.Action(
            name="enable",
            label=_(u"Enable Syndication"),
            condition="allowed",
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

    @memoize
    def getContent(self):
        return getAdapter(self.context, ISyndicationInfo)

    @memoize
    def disabled(self, action=None):
        return not self.enabled()

    @memoize
    def enabled(self, action=None):
        return self.getContent().enabled

    def setUpWidgets(self, ignore_request=False):
        if not self.allowed():
            self.form_fields = form.FormFields()
            self.widgets = {}
            return
        super(Folder, self).setUpWidgets(ignore_request)
        self.widgets['enabled'].hide = True

    @memoize
    def allowed(self, action=None):
        return self.getContent().allowed

    def applyChanges(self, data):
        return form.applyData(self.context, self.form_fields, data,
                          self.adapters)

    def handle_enable(self, action, data):
        self.getContent().enable()
        self._handle_success(action, data)
        self.status = _(u"Syndication enabled.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_disable(self, action, data):
        self.getContent().disable()
        self.status = _(u"Syndication disabled.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_change(self, action, data):
        self._handle_success(action, data)
        self.status = _(u"Syndication settings changed.")
        self._setRedirect("portal_actions", "object/syndication")

    def handle_revert(self, action, data):
        self.getContent().revert()
        self.status = _(u"Syndication reset to site default.")
        self._setRedirect("portal_actions", "object/syndication")
