#############################################################################
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
"""Join form.
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.formlib import form
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Password

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.permissions import ManageUsers
from Products.CMFDefault.utils import Message as _


class IJoinSchema(Interface):

    """Schema for join form.
    """

    member_id = ASCIILine(
        title=_(u"Member ID"))

    email = EmailLine(
        title=_(u"Email Address"))

    password = Password(
        title=_(u"Password"),
        min_length=5)

    confirmation = Password(
        title=_(u"Password (confirm)"),
        min_length=5)

    send_password = Bool(
        title=_(u"Mail Password?"),
        description=_(u"Check this box to have the password mailed."))

    @invariant
    def check_passwords_match(schema):
        """Password and confirmation must match"""
        if schema.password != schema.confirmation:
            raise Invalid(_(u"Your password and confirmation did not match. "
                            u"Please try again."))


class JoinFormView(EditFormBase):

    base_template = EditFormBase.template
    template = ViewPageTemplateFile("join.pt")
    registered = False
    form_fields = form.FormFields(IJoinSchema)

    actions = form.Actions(
        form.Action(
            name='register',
            label=_(u'Register'),
            validator='handle_register_validate',
            success='handle_register_success',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel'),
            validator='handle_cancel_validate',
            success='handle_cancel_success',
            failure='handle_cancel_failure'))

    def __init__(self, context, request):
        super(JoinFormView, self).__init__(context, request)
        if self.validate_email:
            self.form_fields = self.form_fields.select('member_id', 'email')
        self.rtool = self._getTool('portal_registration')
        self.mtool = self._getTool('portal_membership')

    @property
    @memoize
    def validate_email(self):
        ptool = getUtility(IPropertiesTool)
        return ptool.getProperty('validate_email')

    @property
    @memoize
    def isAnon(self):
        return self.mtool.isAnonymousUser()

    @property
    @memoize
    def isManager(self):
        return self.mtool.checkPermission(ManageUsers, self.mtool)

    @property
    @memoize
    def isOrdinaryMember(self):
        return not (self.registered or self.isManager or self.isAnon)

    @property
    def title(self):
        if self.isManager:
            return _(u'Register a New Member')
        else:
            return _(u'Become a Member')

    def setUpWidgets(self, ignore_request=False):
        """If email validation is in effect, users cannot select passwords"""
        super(JoinFormView, self).setUpWidgets(ignore_request)

    def personalize(self):
        atool = self._getTool('portal_actions')
        return atool.getActionInfo("user/preferences")['url']

    def handle_register_validate(self, action, data):
        """Avoid duplicate registration"""
        errors = self.validate(action, data)
        member = self.mtool.getMemberById(data.get('member_id', None))
        if member is not None:
            errors.append(_(u"The login name you selected is already in use "
                            u"or is not valid. Please choose another."))
        return errors

    def add_member(self, data):
        """Add new member and notify if requested or required"""
        self.rtool.addMember(
                        id=data['member_id'],
                        password=data['password'],
                             properties={
                                        'username': data['member_id'],
                                        'email': data['email']
                                        }
                        )
        if self.validate_email or data['send_password']:
            self.rtool.registeredNotify(data['member_id'])
        self.registered = True
        self.label = _(u'Success')

    def handle_register_success(self, action, data):
        """Register user and inform they have been registered"""
        if self.validate_email:
            data['password'] = self.rtool.generatePassword()
        self.add_member(data)
        self.status = _(u'You have been registered as a member.')
        if not self.validate_email:
            self._setRedirect('portal_actions', 'user/login')

    def handle_cancel_validate(self, action, data):
        return []

    def handle_cancel_success(self, action, data):
        return self._setRedirect('portal_actions', 'global/manage_members',
                                 keys='b_start')

    def handle_cancel_failure(self, action, data, errors):
        self.status = None
        return self._setRedirect('portal_actions', 'global/manage_members',
                                 keys='b_start')
