##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Formlib form base classes.

$Id$
"""

from datetime import datetime
from sets import Set

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.formlib.formbase import PageAddForm
from Products.Five.formlib.formbase import PageDisplayForm
from Products.Five.formlib.formbase import PageForm
from zope.app.container.interfaces import INameChooser
from zope.component import adapts
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.datetime import parseDatetimetz
from zope.formlib import form
from zope.formlib.interfaces import IPageForm
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import LoadLocaleError
from zope.i18n.locales import locales
from zope.interface import implementsOnly
from ZTUtils import make_query

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFDefault.browser.utils import ViewBase
from Products.CMFDefault.exceptions import AccessControl_Unauthorized
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.utils import translate


# from zope.publisher.http.HTTPRequest
def _getLocale(request):
    envadapter = IUserPreferredLanguages(request, None)
    if envadapter is None:
        return None

    langs = envadapter.getPreferredLanguages()
    for httplang in langs:
        parts = (httplang.split('-') + [None, None])[:3]
        try:
            return locales.getLocale(*parts)
        except LoadLocaleError:
            # Just try the next combination
            pass
    else:
        # No combination gave us an existing locale, so use the default,
        # which is guaranteed to exist
        return locales.getLocale(None, None, None)


class _EditFormMixin(ViewBase):

    template = ViewPageTemplateFile('editform.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # BBB: for Zope 2.10
        if getattr(self.request, 'locale', None) is None:
            self.request.locale = _getLocale(request)

    def _setRedirect(self, provider_id, action_path, keys=''):
        provider = self._getTool(provider_id)
        try:
            target = provider.getActionInfo(action_path, self.context)['url']
        except ValueError:
            target = self._getPortalURL()

        kw = {}
        if self.status:
            message = translate(self.status, self.context)
            if isinstance(message, unicode):
                message = message.encode(self._getBrowserCharset())
            kw['portal_status_message'] = message
        for k in keys.split(','):
            k = k.strip()
            v = self.request.form.get(k, None)
            if v:
                kw[k] = v

        query = kw and ( '?%s' % make_query(kw) ) or ''
        self.request.RESPONSE.redirect( '%s%s' % (target, query) )

        return ''

    def handle_failure(self, action, data, errors):
        if self.status:
            message = translate(self.status, self.context)
            self.request.other['portal_status_message'] = message


class EditFormBase(_EditFormMixin, PageForm):

    pass


class ContentAddFormBase(_EditFormMixin, PageAddForm):

    adapts(IFolderish, ICMFDefaultSkin, ITypeInformation)
    implementsOnly(IPageForm)

    actions = form.Actions(
        form.Action(
            name='add',
            label=form._('Add'),
            condition=form.haveInputWidgets,
            success='handle_add',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel'),
            success='handle_cancel_success',
            failure='handle_cancel_failure'))

    def __init__(self, context, request, ti):
        self.context = context
        self.request = request
        self.ti = ti
        # BBB: for Zope 2.10
        if getattr(self.request, 'locale', None) is None:
            self.request.locale = _getLocale(request)

    @property
    def label(self):
        obj_type = translate(self.ti.Title(), self.context)
        return _(u'Add ${obj_type}', mapping={'obj_type': obj_type})

    @property
    def description(self):
        return self.ti.Description()

    #same as in form.AddFormBase but without action decorator
    def handle_add(self, action, data):
        self.createAndAdd(data)

    def handle_cancel_success(self, action, data):
        return self._setRedirect('portal_types',
                                 ('object/folderContents', 'object/view'))

    def handle_cancel_failure(self, action, data, errors):
        self.status = None
        return self._setRedirect('portal_types',
                                 ('object/folderContents', 'object/view'))

    def create(self, data):
        id =  data.pop('id', '') or ''
        factory = getUtility(IFactory, self.ti.factory)
        obj = factory(id=id, **data)
        obj._setPortalTypeName(self.ti.getId())
        return obj

    def add(self, obj):
        container = self.context
        portal_type = self.ti.getId()

        # check allowed (sometimes redundant, but better safe than sorry)
        if not self.ti.isConstructionAllowed(container):
            raise AccessControl_Unauthorized('Cannot create %s' % portal_type)

        #check container constraints
        ttool = self._getTool('portal_types')
        container_ti = ttool.getTypeInfo(container)
        if container_ti is not None and \
                not container_ti.allowType(portal_type):
            raise ValueError('Disallowed subobject type: %s' % portal_type)

        name = INameChooser(container).chooseName(obj.getId(), obj)
        obj.id = name
        container._setObject(name, obj)
        obj = container._getOb(name)

        obj_type = translate(obj.Type(), container)
        self.status = _(u'${obj_type} added.', mapping={'obj_type': obj_type})
        self._finished_add = True
        self._added_obj = obj
        return obj

    def nextURL(self):
        obj = self._added_obj

        message = translate(self.status, self.context)
        if isinstance(message, unicode):
            message = message.encode(self._getBrowserCharset())
        return '%s/%s?%s' % (obj.absolute_url(), self.ti.immediate_view,
                             make_query(portal_status_message=message))


class ContentEditFormBase(_EditFormMixin, PageForm):

    actions = form.Actions(
        form.Action(
            name='change',
            label=_(u'Change'),
            validator='handle_validate',
            success='handle_change_success',
            failure='handle_failure'),
        form.Action(
            name='change_and_view',
            label=_(u'Change and View'),
            validator='handle_validate',
            success='handle_change_and_view_success',
            failure='handle_failure'))

    description = u''

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @property
    def label(self):
        obj_type = translate(self.context.Type(), self.context)
        return _(u'Edit ${obj_type}', mapping={'obj_type': obj_type})

    def handle_validate(self, action, data):
        if self.context.wl_isLocked():
            return (_(u'This resource is locked via webDAV.'),)
        return None

    def _handle_success(self, action, data):
        # normalize set and datetime
        for k, v in data.iteritems():
            if isinstance(v, Set):
                data[k] = set(v)
            elif isinstance(v, datetime) and v.tzname() is None:
                data[k] = parseDatetimetz(str(v))
        changed = form.applyChanges(self.context, self.form_fields, data,
                                    self.adapters)
        if changed:
            self.context.reindexObject()
            obj_type = translate(self.context.Type(), self.context)
            self.status = _(u'${obj_type} changed.',
                            mapping={'obj_type': obj_type})
        else:
            self.status = _(u'Nothing to change.')
        return changed

    def handle_change_success(self, action, data):
        self._handle_success(action, data)
        return self._setRedirect('portal_types', 'object/edit')

    def handle_change_and_view_success(self, action, data):
        self._handle_success(action, data)
        return self._setRedirect('portal_types', 'object/view')


class DisplayFormBase(PageDisplayForm, ViewBase):

    template = ViewPageTemplateFile('viewform.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # BBB: for Zope 2.10
        if getattr(self.request, 'locale', None) is None:
            self.request.locale = _getLocale(request)

    @property
    def label(self):
        return self.context.Type()
