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
"""Change password form.
"""

from DateTime import DateTime
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema import Password

from Products.CMFCore.interfaces import IMember
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.utils import decode
from Products.CMFDefault.formlib.form import SettingsEditFormBase
from Products.CMFDefault.utils import Message as _


class IPasswordSchema(Interface):

    password = Password(
                    title=_(u"New password"),
                    min_length=5
                    )

    confirmation = Password(
                    title=_(u"Confirm new password"),
                    required=False
                    )

    @invariant
    def check_passwords_match(schema):
        """Password and confirmation must match"""
        if schema.password != schema.confirmation:
            raise Invalid(_(u"Your password and confirmation did not match. "
                            u"Please try again."))


class PasswordSchemaAdapter(object):

    adapts(IMember)
    implements(IPasswordSchema)

    def __init__(self, context):
        self.context = context

    def _getPassword(self):
        return u''

    def _setPassword(self, val):
        self.context.setSecurityProfile(val)

    def _getLastLoginTime(self):
        return self.context.getProperty('last_login_time')

    def _setLastLoginTime(self, val):
        self.context.setProperties(last_login_time=val)

    password = property(_getPassword, _setPassword)
    confirmation = u''
    last_login_time = property(_getLastLoginTime, _setLastLoginTime)


class PasswordFormView(SettingsEditFormBase):

    successMessage = _(u"Your password has been changed.")
    form_fields = form.FormFields(IPasswordSchema)

    @property
    def label(self):
        if self.is_first_login:
            return _(u'Welcome!')
        else:
            return _(u'Change your Password')

    @property
    @decode
    def portal_title(self):
        return getUtility(ISiteRoot).title

    @property
    def description(self):
        if self.is_first_login:
            return _(u"This is the first time that you've logged in to "
                     u"${portal_title}. Before you start exploring you need "
                     u"to change your original password. This will ensure "
                     u"that the password we sent you via email cannot be "
                     u"used in a malicious manner.",
                     mapping={'portal_title': self.portal_title})
        else:
            return _(u'Please use the form below to change your password.')

    @memoize
    def getContent(self):
        mtool = self._getTool('portal_membership')
        member = mtool.getAuthenticatedMember()
        return PasswordSchemaAdapter(member)

    @property
    def is_first_login(self):
        return self.getContent().last_login_time == DateTime('1999/01/01')

    def applyChanges(self, data):
        changes = super(PasswordFormView, self).applyChanges(data)
        if self.getContent().last_login_time == DateTime('1999/01/01'):
            self.getContent().last_login_time = DateTime('2000/01/01')
        mtool = self._getTool('portal_membership')
        mtool.credentialsChanged(data['password'], self.request)
        return changes

    def handle_change_success(self, action, data):
        self._handle_success(action, data)
        return self._setRedirect('portal_actions', 'user/mystuff')

    def handle_cancel_success(self, action, data):
        return self._setRedirect('portal_actions', 'user/mystuff')
