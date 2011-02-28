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
"""

from urllib import quote, urlencode

from DateTime import DateTime
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Forbidden
from zExceptions import Redirect
from zope.formlib import form
from zope.formlib.widgets import TextWidget
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Password
from zope.schema import TextLine
from zope.schema import URI
from zope.schema.interfaces import ISource
from zope.site.hooks import getSite

from Products.CMFCore.CookieCrumbler import ATTEMPT_LOGIN
from Products.CMFCore.CookieCrumbler import ATTEMPT_NONE
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import ViewBase, memoize


def _expireAuthCookie(view):
    try:
        cctool = getToolByName(view, 'cookie_authentication')
        method = cctool.getCookieMethod('expireAuthCookie',
                                        cctool.defaultExpireAuthCookie)
        method(view.request.response, cctool.auth_cookie)
    except AttributeError:
        view.request.response.expireCookie('__ac', path='/')


class UnauthorizedView(BrowserView):

    """Exception view for Unauthorized.
    """

    forbidden_template = ViewPageTemplateFile('forbidden.pt')

    def __call__(self):
        try:
            atool = getToolByName(self, 'portal_actions')
            target = atool.getActionInfo('user/login')['url']
        except (AttributeError, ValueError):
            # re-raise the unhandled exception
            raise self.context

        req = self.request
        attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)
        if attempt not in (ATTEMPT_NONE, ATTEMPT_LOGIN):
            # An authenticated user was denied access to something.
            # XXX: hack context to get the right @@standard_macros/page
            #      why do we get the wrong without this hack?
            self.context = self.__parent__
            raise Forbidden(self.forbidden_template())

        _expireAuthCookie(self)
        came_from = req.get('came_from', None)
        if came_from is None:
            came_from = req.get('ACTUAL_URL')
            query = req.get('QUERY_STRING')
            if query:
                # Include the query string in came_from
                if not query.startswith('?'):
                    query = '?' + query
                came_from = came_from + query
        url = '%s?came_from=%s' % (target, quote(came_from))
        raise Redirect(url)


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

    name = TextLine(
        title=_(u'Member ID'),
        description=_(u'Case sensitive'))

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
    template = ViewPageTemplateFile('login.pt')
    label = _(u'Log in')
    prefix = ''

    form_fields = form.FormFields(ILoginSchema)

    actions = form.Actions(
        form.Action(
            name='login',
            label=_(u'Login'),
            validator='handle_login_validate',
            success='handle_login_success',
            failure='handle_failure'))

    def setUpWidgets(self, ignore_request=False):
        try:
            cctool = self._getTool('cookie_authentication')
            ac_name_id = cctool.name_cookie
            ac_password_id = cctool.pw_cookie
            ac_persistent_id = cctool.persist_cookie
        except AttributeError:
            ac_name_id = '__ac_name'
            ac_password_id = '__ac_password'
            ac_persistent_id = '__ac_persistent'
        ac_name = self.request.get(ac_name_id)
        if ac_name is not None:
            self.request.form['name'] = ac_name
            self.request.form[ac_name_id] = ac_name
        ac_persistent = self.request.get(ac_persistent_id)
        if ac_persistent is not None:
            self.request.form['persistent'] = ac_persistent
        ac_persistent_used = self.request.get("%s.used" % ac_persistent_id)
        if ac_persistent_used is not None:
            self.request.form['persistent.used'] = ac_persistent_used
        super(LoginFormView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['came_from'].hide = True
        self.widgets['name'].name = ac_name_id
        self.widgets['password'].name = ac_password_id
        self.widgets['persistent'].name = ac_persistent_id

    def handle_login_validate(self, action, data):
        mtool = self._getTool('portal_membership')
        if mtool.isAnonymousUser():
            _expireAuthCookie(self)
            return (_(u'Login failure'),)
        return None

    def handle_login_success(self, action, data):
        return self._setRedirect('portal_actions', 'user/logged_in',
                                 'came_from')

class LoggedIn(ViewBase):
    """Post login methods"""

    template = ViewPageTemplateFile("logged_in.pt")

    def set_skin_cookie(self):
        stool = self._getTool('portal_skins')
        if stool.updateSkinCookie():
            skinname = stool.getSkinNameFromRequest(self.request)
            stool.changeSkin(skinname, self.request)

    def first_login(self, member):
        """First time login, reset password"""
        utool = self._getTool('portal_url')
        now = DateTime()
        member.setProperties(last_login_time='1999/01/01', login_time=now)
        target = '%s/password_form' % utool()
        return self.request.response.redirect(target)

    def __call__(self):
        self.set_skin_cookie()
        mtool = self._getTool('portal_membership')
        mtool.createMemberArea()
        member = mtool.getAuthenticatedMember()
        now = DateTime()
        last_login = member.getProperty('login_time', None)
        never_logged_in = str(last_login).startswith('2000/01/01')
        ptool = self._getTool('portal_properties')
        if never_logged_in and ptool.getProperty('validate_email'):
            return self.first_login(member)
        else:
            member.setProperties(last_login_time=last_login, login_time=now)
        came_from = self.request.get('came_from', None)
        if came_from:
            return self.request.response.redirect(came_from)
        return self.template()


class MailPasswordFormView(EditFormBase):

    """Form view for IMailPasswordSchema.
    """

    base_template = EditFormBase.template
    template = ViewPageTemplateFile('mail_password.pt')
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
        try:
            cctool = self._getTool('cookie_authentication')
            ac_name_id = cctool.name_cookie
        except AttributeError:
            ac_name_id = '__ac_name'
        ac_name = self.request.get(ac_name_id)
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


class Logout(ViewBase):
    """Log the user out"""

    template = ViewPageTemplateFile("logged_out.pt")

    @memoize
    def logged_in(self):
        """Check whether the user is (still logged in)"""
        mtool = self._getTool('portal_membership')
        return not mtool.isAnonymousUser()

    @memoize
    def logout(self):
        """Log the user out"""
        _expireAuthCookie(self)

    @memoize
    def clear_skin_cookie(self):
        """Remove skin cookie"""
        stool = self._getTool('portal_skins')
        stool.clearSkinCookie()

    def __call__(self):
        """Clear cookies and return the template"""
        if 'portal_status_message' in self.request:
            return self.template()
        if self.logged_in():
            self.clear_skin_cookie()
            self.logout()
            status = "?" + urlencode({'portal_status_message':
                                      _(u'You have been logged out.')})
            return self.request.response.redirect(self.request.URL + status)
