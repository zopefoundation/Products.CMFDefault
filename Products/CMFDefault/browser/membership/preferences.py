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

from zope.formlib import form
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.utils import Message as _


def portal_skins(context):
    stool = getToolByName(context, 'portal_skins')
    return SimpleVocabulary.fromValues(stool.getSkinSelections())


class IPreferencesSchema(Interface):

    email = EmailLine(
        title=_(u"Email Address"))

    listed = Bool(
        title=_(u"Listed status"),
        description=_(u"Select to be listed on the public membership roster."))

    portal_skin = Choice(
        title=_(u"Skin"),
        vocabulary=u"cmf.portal_skins",
        required=False)


class Preferences(EditFormBase):

    form_fields = form.FormFields(IPreferencesSchema)

    actions = form.Actions(
                form.Action(
                name="change",
                label=u"Change",
                success="handle_success",
                failure="handle_failure"
                    )
                )
    label = _(u"Member preferences")

    def __init__(self, context, request):
        super(Preferences, self).__init__(context, request)
        self.mtool = self._getTool('portal_membership')
        self.stool = self._getTool('portal_skins')
        self.atool = self._getTool('portal_actions')

    def get_skin_cookie(self):
        """Check for user cookie"""
        cookies = self.request.cookies
        return cookies.get('portal_skin')

    @property
    def member(self):
        """Get the current user"""
        return self.mtool.getAuthenticatedMember()

    def setUpWidgets(self, ignore_request=False):
        """Populate form with member preferences"""
        data = {}
        data['email'] = self.member.email
        data['listed'] = getattr(self.member, 'listed', None)
        data['portal_skin'] = self.get_skin_cookie()

        self.widgets = form.setUpDataWidgets(self.form_fields,
                                        self.prefix,
                                        self.context,
                                        self.request,
                                        data=data,
                                        ignore_request=False)

    def handle_success(self, action, data):
        if 'portal_skin' in data:
            self.stool.portal_skins.updateSkinCookie()
        self.member.setProperties(data)
        self.status = _(u"Member preferences changed.")
        self._setRedirect('portal_actions', 'user/preferences')
