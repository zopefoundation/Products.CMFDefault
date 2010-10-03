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

"""Enable or disable site syndication"""

from zope.component import getAdapter
from zope.interface import Interface
from zope.formlib import form
from zope.schema import Choice, Int, Datetime
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import memoize


frequency_vocab = SimpleVocabulary.fromItems(
                            [(_(u'Hourly'), 'hourly'),
                             (_(u'Daily'), 'daily'),
                             (_(u'Weekly'), 'weekly'),
                             (_(u'Monthly'), 'monthly'),
                             (_(u'Yearly'), 'yearly')
                            ])


class ISyndicationSchema(Interface):
    """Syndication form schema"""
    
    period = Choice(
                    title=_(u"Update period"),
                    vocabulary=frequency_vocab,
                    default="daily"
                    )
    
    frequency = Int(
                title=_(u"Update frequency"),
                description=_(u"This is a multiple of the update period. An"
                    u" update frequency of '3' and an update period"
                    u" of 'Monthly' will mean an update every three months.")
                    )
    
    base = Datetime(
                title=_(u"Update base"),
                description=_(u"")
                )
    
    max_items = Int(
                title=_(u"Maximum number of items"),
                description=_(u"")
                )

class Site(EditFormBase):
    """Enable or disable syndication for a site."""
    
    
    form_fields = form.FormFields(ISyndicationSchema)
    actions = form.Actions(
                form.Action(
                    name="enable",
                    label=_(u"Enable syndication"),
                    condition="disabled",
                    success="handle_enable",
                    ),
                form.Action(
                    name="update",
                    label=_(u"Update syndication"),
                    condition="enabled",
                    success="handle_update",
                    ),
                form.Action(
                    name="disable",
                    label=_(u"Disable syndication"),
                    condition="enabled",
                    success="handle_disable"
                    )
                )
    
    @property
    @memoize
    def syndtool(self):
        return self._getTool("portal_syndication")
    
    @memoize
    def enabled(self, action=None):
        return self.syndtool.isAllowed
    
    @memoize
    def disabled(self, action=None):
        return not self.syndtool.isAllowed
    
    def setUpWidgets(self, ignore_request=False):
        data = {'frequency':self.syndtool.syUpdateFrequency,
                'period':self.syndtool.syUpdatePeriod,
                'base':self.syndtool.syUpdateBase,
                'max_items':self.syndtool.max_items
               }
        self.widgets = form.setUpDataWidgets(self.form_fields, self.prefix,
                       self.context, self.request,data=data,
                       ignore_request=ignore_request)
    
    def handle_enable(self, action, data):
        self.handle_update(action, data)
        self.syndtool.isAllowed = 1
        self.status = _(u"Syndication enabled")
        self._setRedirect("portal_actions", "global/syndication")
    
    def handle_update(self, action, data):
        self.syndtool.editProperties(updatePeriod=data['period'],
                                    updateFrequency=data['frequency'],
                                    updateBase=data['base'],
                                    max_items=data['max_items']
                                    )
        self.status = _(u"Syndication updated")
        self._setRedirect("portal_actions", "global/syndication")
    
    def handle_disable(self, action, data):
        self.syndtool.isAllowed = 0
        self.status = _(u"Syndication disabled")
        self._setRedirect("portal_actions", "global/syndication")


class Syndicate(EditFormBase):
    """
    Enable, disable and customise syndication settings for a folder
    """
    
    form_fields = form.FormFields(ISyndicationSchema)
    
    actions = form.Actions(
                form.Action(
                    name="enable",
                    label=_(u"Enable syndication"),
                    condition="disabled",
                    success="handle_enable",
                    ),
                form.Action(
                    name="update",
                    label=_(u"Update syndication"),
                    condition="enabled",
                    success="handle_update",
                    ),
                form.Action(
                    name="revert",
                    label=_(u"Revert to site default"),
                    condition="enabled",
                    success="handle_revert",
                    ),
                form.Action(
                    name="disable",
                    label=_(u"Disable syndication"),
                    condition="enabled",
                    success="handle_disable",
                    validator="validation_disabled"
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
        self.widgets = form.setUpDataWidgets(fields, self.prefix,
                       self.context, self.request,
                       data=self.adapter.get_info(),
                       ignore_request=ignore_request)
    
    def enabled(self, action=None):
        return self.adapter.enabled
    
    def disabled(self, action=None):
        return not self.adapter.enabled
    
    def validation_disabled(self, action, data):
        """Do nothing, data is irrelevant"""
        pass
    
    def handle_enable(self, action, data):
        self.adapter.enable()
        self.status = _(u"Syndication enabled for ")
        self._setRedirect("portal_actions", "folder/syndication")
    
    def handle_disable(self, action, data):
        self.adapter.disable()
        self.status = _(u"Syndication disabled for")
        self._setRedirect("portal_actions", "folder/syndication")
    
    def handle_update(self, action, data):
        self.adapter.set_info(**data)
        self.status = _(u"Syndication updated for")
        self._setRedirect("portal_actions", "folder/syndication")
    
    def handle_revert(self, action, data):
        self.adapter.revert()
        self.status = _(u"Syndication reset to site default")
        self._setRedirect("portal_actions", "folder/syndication")