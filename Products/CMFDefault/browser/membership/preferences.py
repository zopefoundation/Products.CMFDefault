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
"""Change user preferences.
"""

from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.interfaces import IMember
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.formlib.form import SettingsEditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.utils import Message as _


def portal_skins(context):
    stool = getToolByName(context.context, 'portal_skins')
    return SimpleVocabulary.fromValues(stool.getSkinSelections())


class IPreferencesSchema(Interface):

    email = EmailLine(
        title=_(u"Email Address"))

    listed = Bool(
        title=_(u"Listed status"),
        description=_(u"Select to be listed on the public membership roster."))

    portal_skin = Choice(
        title=_(u"Skin"),
        vocabulary=u"cmf.AvailableSkins",
        required=False,
        missing_value='')


class PreferencesSchemaAdapter(object):

    """Adapter for IMember.
    """

    adapts(IMember)
    implements(IPreferencesSchema)

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        return self.context.getProperty(name)

    def __setattr__(self, name, value):
        if name in ('email', 'listed', 'portal_skin'):
            self.context.setMemberProperties({name: value})
        else:
            object.__setattr__(self, name, value)


class Preferences(SettingsEditFormBase):

    label = _(u"Member Preferences")
    successMessage = _(u"Member preferences changed.")

    form_fields = form.FormFields(IPreferencesSchema)

    @memoize
    def getContent(self):
        mtool = self._getTool('portal_membership')
        member = mtool.getAuthenticatedMember()
        return PreferencesSchemaAdapter(member)

    def applyChanges(self, data):
        changes = super(Preferences, self).applyChanges(data)
        if any('portal_skin' in v for v in changes.itervalues()):
            stool = self._getTool('portal_skins')
            stool.updateSkinCookie()
        return changes

    def handle_change_success(self, action, data):
        self._handle_success(action, data)
        return self._setRedirect('portal_actions', 'user/preferences')
