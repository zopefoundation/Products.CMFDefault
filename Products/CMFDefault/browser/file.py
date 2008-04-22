##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for files.

$Id$
"""

from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Bytes
from zope.schema import Text
from zope.schema import TextLine

from Products.CMFDefault.formlib.form import ContentAddFormBase
from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.interfaces import IMutableFile
from Products.CMFDefault.utils import Message as _


class IFileSchema(Interface):

    """Schema for file views.
    """

    title = TextLine(
        title=_(u'Title'),
        required=False,
        missing_value=u'')

    language = TextLine(
        title=_(u'Language'),
        required=False,
        missing_value=u'',
        max_length=2)

    description = Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'')

    format = ASCIILine(
        title=_(u'Content type'),
        readonly=True)

    upload = Bytes(
        title=_(u'Upload'),
        required=False)


class FileSchemaAdapter(SchemaAdapterBase):

    """Adapter for IMutableFile.
    """

    adapts(IMutableFile)
    implements(IFileSchema)

    _upload = ProxyFieldProperty(IFileSchema['upload'], 'data')

    def _setUpload(self, value):
        self.context.manage_upload(value)

    title = ProxyFieldProperty(IFileSchema['title'], 'Title', 'setTitle')
    language = ProxyFieldProperty(IFileSchema['language'],
                                  'Language', 'setLanguage')
    description = ProxyFieldProperty(IFileSchema['description'],
                                     'Description', 'setDescription')
    format = ProxyFieldProperty(IFileSchema['format'], 'Format')
    upload = property(_upload.__get__, _setUpload)


class FileAddView(ContentAddFormBase):

    """Add view for IMutableFile.
    """

    form_fields = (
        form.FormFields(IFileSchema).select('title', 'description') +
        form.FormFields(Bytes(__name__='upload', title=_(u'Upload')),
                        TextLine(__name__='portal_type', default=u'File'))
        )

    def setUpWidgets(self, ignore_request=False):
        super(FileAddView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['description'].height = 3
        self.widgets['portal_type'].hide = True
        self.widgets['upload'].displayWidth = 60

    def finishCreate(self, obj, data):
        adapted = FileSchemaAdapter(obj)
        adapted.language = u''
        adapted.upload = self.request.form['%s.upload' % self.prefix]
        if data['title']:
            adapted.title = data['title']
        if data['description']:
            adapted.description = data['description']
        return obj


class FileEditView(ContentEditFormBase):

    """Edit view for IMutableFile.
    """

    form_fields = form.FormFields(IFileSchema).omit('language')

    def setUpWidgets(self, ignore_request=False):
        super(FileEditView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['description'].height = 3
        self.widgets['upload'].displayWidth = 60

    def _handle_success(self, action, data):
        if data.get('upload'):
            data['upload'] = self.request.form['%s.upload' % self.prefix]
        else:
            del data['upload']
        return super(FileEditView, self)._handle_success(action, data)
