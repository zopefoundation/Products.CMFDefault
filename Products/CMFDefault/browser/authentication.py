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
"""Authentication browser views.

$Id$
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.form.browser import TextWidget
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Password
from zope.schema import URI
from zope.schema.interfaces import ISource
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _


class NameSource(object):

    implements(ISource)

    def __contains__(self, value):
        rich_context = getSite()
        mtool = getToolByName(rich_context, 'portal_membership')
        if mtool.getMemberById(value):
            return True
        candidates = mtool.searchMembers('email', value)
        for candidate in candidates:
            if candidate['email'].lower() == value.lower():
                return True
        return False

available_names = NameSource()


class ILoginSchema(Interface):

    """Schema for login form.
    """

    came_from = URI(
        required=False)

    name = Choice(
        title=_(u'Member ID'),
        description=_(u'Member ID or email address'),
        source=available_names)

    password = Password(
        title=_(u'Password'),
        description=_(u'Case sensitive'))

    persistent = Bool(
        title=_(u'Remember my ID.'),
        description=_(u'Saves your member ID in a cookie.'),
        default=True)


class IMailPasswordSchema(Interface):

    """Schema for mail password form.
    """

    name = Choice(
        title=_(u'Member ID'),
        description=_(u'Member ID or email address'),
        source=available_names)


class LoginFormView(EditFormBase):

    """Form view for ILoginSchema.
    """

    base_template = EditFormBase.template
    template = ViewPageTemplateFile('templates/login.pt')
    label = _(u'Log in')

    form_fields = form.FormFields(ILoginSchema)
    form_fields['name'].custom_widget = TextWidget

    actions = form.Actions(
        form.Action(
            name='login',
            label=_(u'Login'),
            success='handle_login_success',
            failure='handle_failure'))

    def setUpWidgets(self, ignore_request=False):
        ac_name = self.request.get('__ac_name')
        if ac_name and not self.request.has_key('%s.name' % self.prefix):
            self.request.form['%s.name' % self.prefix] = ac_name
        super(LoginFormView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['came_from'].hide = True

    def handle_login_success(self, action, data):
        mtool = self._getTool('portal_membership')
        if not mtool.getMemberById(data['name']):
            candidates = mtool.searchMembers('email', data['name'])
            for candidate in candidates:
                if candidate['email'].lower() == data['name'].lower():
                    data['name'] = candidate['username']
                    break
        # logged_in uses default charset for decoding
        charset = self._getDefaultCharset()
        self.request.form['__ac_name'] = data['name'].encode(charset)
        self.request.form['__ac_password'] = data['password'].encode(charset)
        self.request.form['__ac_persistent'] = data['persistent']
        cctool = self._getTool('cookie_authentication')
        cctool(self.context, self.request)
        return self._setRedirect('portal_actions', 'user/logged_in',
                                 '%s.came_from' % self.prefix)


class MailPasswordFormView(EditFormBase):

    """Form view for IMailPasswordSchema.
    """

    base_template = EditFormBase.template
    template = ViewPageTemplateFile('templates/mail_password.pt')
    label = _(u"Don't panic!")
    description = _(u"Just enter your member ID below, click 'Send', and "
                    u"your password will be mailed to you if you gave a "
                    u"valid email address when you signed on.")

    form_fields = form.FormFields(IMailPasswordSchema)
    form_fields['name'].custom_widget = TextWidget

    actions = form.Actions(
        form.Action(
            name='send',
            label=_(u'Send'),
            success='handle_send_success',
            failure='handle_failure'))

    def setUpWidgets(self, ignore_request=False):
        ac_name = self.request.get('__ac_name')
        if ac_name and not self.request.has_key('%s.name' % self.prefix):
            self.request.form['%s.name' % self.prefix] = ac_name
        super(MailPasswordFormView,
              self).setUpWidgets(ignore_request=ignore_request)

    def handle_send_success(self, action, data):
        mtool = self._getTool('portal_membership')
        if not mtool.getMemberById(data['name']):
            candidates = mtool.searchMembers('email', data['name'])
            for candidate in candidates:
                if candidate['email'].lower() == data['name'].lower():
                    data['name'] = candidate['username']
                    break
        rtool = self._getTool('portal_registration')
        rtool.mailPassword(data['name'], self.request)
        self.status = _(u'Your password has been mailed to you.')
        return self._setRedirect('portal_actions', 'user/login')
