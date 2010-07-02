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

from zope.formlib import form
from zope.interface import Interface, invariant
from zope.schema import ASCIILine, Password, List, TextLine

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.formlib.form import EditFormBase

def check_domain(value):
    if " " in value:
        return False
    return True


class IPasswordSchema(Interface):

    password = Password(
                    title=_(u"New password"),
                    min_length=5,
                    required=False
                    )

    confirmation = Password(
                    title=_(u"Confirm new password"),
                    required=False
                    )

    domains = List(
                    title=_("Domains"),
                    description=_(u"""If you do not know what this field is
                                      for, leave it blank."""),
                    value_type=ASCIILine(
                            title=_(u"Domain name"),
                            constraint=check_domain
                            ),
                    required = False
                )

    @invariant
    def check_passwords_match(schema):
        """Password and confirmation must match"""
        if schema.password != schema.confirmation:
            raise Invalid(_(u"Passwords do not match"))


class Password(EditFormBase):

    form_fields = form.FormFields(IPasswordSchema)

    actions = form.Actions(
                    form.Action(
                        name="change",
                        label=_(u"Change password"),
                        success="handle_success",
                        failure="handle_failure"
                        )
                    )

    template = ViewPageTemplateFile("password.pt")
    base_template = EditFormBase.template

    def __init__(self, context, request):
        super(Password, self).__init__(context, request)
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.rtool = getToolByName(self.context, 'portal_registration')
        if self.member.getProperty('last_login_time') == DateTime('1999/01/01'):
            self.member.setProperties(last_login_time='2000/01/01')

    def setUpWidgets(self, ignore_request=False):
        """Populate form with user domains"""
        data = {}
        data['domains'] = " ".join(self.member.getDomains())
        self.widgets = form.setUpDataWidgets(
                            self.form_fields,
                            self.prefix,
                            self.context,
                            self.request,
                            data=data,
                            ignore_request=ignore_request)

    @property
    def member(self):
        return self.mtool.getAuthenticatedMember()

    @property
    def is_first_login(self):
        return self.member.getProperty('last_login_time') == DateTime('1999/01/01')

    def handle_success(self, action, data):
        data.pop("confirmation")
        self.member.setSecurityProfile(**data)
        self.status = _(u'Your password has been changed.')
        self._setRedirect("portal_actions", "user/login")
