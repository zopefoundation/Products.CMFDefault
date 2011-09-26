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
"""Portal Configuration Form.
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.formlib import form
from zope.schema import getFieldNames

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget
from Products.CMFDefault.utils import Message as _

from .interfaces import IPortalConfig


class PortalConfig(EditFormBase):

    form_fields = form.FormFields(IPortalConfig)
    form_fields['validate_email'].custom_widget = ChoiceRadioWidget

    actions = form.Actions(
        form.Action(
            name='change',
            label=_(u'Change'),
            success='handle_success',
            failure='handle_failure'),
    )
    template = ViewPageTemplateFile("config.pt")

    def setUpWidgets(self, ignore_request=False):
        data = {}
        ptool = getUtility(IPropertiesTool)
        charset = ptool.getProperty('default_charset', None)
        for name in getFieldNames(IPortalConfig):
            value = ptool.getProperty(name)
            try:
                value = value.decode(charset)
            except (AttributeError, UnicodeEncodeError):
                pass
            data[name] = value
        data['smtp_server'] = ptool.smtp_server()
        self.widgets = form.setUpDataWidgets(
                    self.form_fields, self.prefix,
                    self.context, self.request, data=data,
                    ignore_request=ignore_request)

    def handle_success(self, action, data):
        ptool = getUtility(IPropertiesTool)
        ptool.editProperties(data)
        self.status = _(u"Portal settings changed.")
        self._setRedirect('portal_actions', 'global/configPortal')
