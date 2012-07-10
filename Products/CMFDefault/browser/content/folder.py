##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for folders.
"""

import sys
import urllib

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.formlib import form
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.sequencesort.ssort import sort
from ZTUtils import Batch
from ZTUtils import LazyFilter

from .interfaces import IBatchForm
from .interfaces import IDeltaItem
from .interfaces import IFolderItem
from .interfaces import ISortForm
from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFDefault.browser.utils import decode
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.utils import ViewBase
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.formlib.form import _EditFormMixin
from Products.CMFDefault.permissions import AddPortalContent
from Products.CMFDefault.permissions import DeleteObjects
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.permissions import ViewManagementScreens
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.utils import thousands_commas

def contents_delta_vocabulary(context):
    """Vocabulary for the pulldown for moving objects up and down.
    """
    length = len(context.contentIds())
    deltas = [SimpleTerm(i, str(i), str(i))
            for i in range(1, min(5, length)) + range(5, length, 5)]
    return SimpleVocabulary(deltas)


class BatchViewBase(ViewBase):
    """ Helper class for creating batch-based views.
    """

    _BATCH_SIZE = 25
    hidden_fields = form.FormFields(IBatchForm, ISortForm)
    prefix = ''

    @memoize
    def setUpWidgets(self, ignore_request=False):
        self.hidden_widgets = form.setUpWidgets(self.hidden_fields,
                            self.prefix, self.context, self.request,
                            ignore_request=ignore_request)

    @memoize
    def _getBatchStart(self):
        b_start = self._getHiddenVars().get('b_start', 0)
        return int(b_start)

    @memoize
    def _getBatchObj(self):
        b_start = self._getBatchStart()
        items = self._get_items()
        return Batch(items, self._BATCH_SIZE, b_start, orphan=0)

    @memoize
    def _getHiddenVars(self):
        data = {}
        if hasattr(self, 'hidden_widgets'):
            form.getWidgetsData(self.hidden_widgets, self.prefix, data)
        else:
            data = self.request.form
        return data

    @memoize
    def _getNavigationVars(self):
        return self._getHiddenVars()

    @memoize
    def expand_prefix(self, key,):
        """Return a form specific query key for use in GET strings"""
        return "%s%s" % (form.expandPrefix(self.prefix), key)

    @memoize
    def _getNavigationURL(self, b_start=None):
        target = self._getViewURL()
        kw = self._getNavigationVars().copy()
        if 'bstart' not in kw:
            kw['b_start'] = b_start

        for k, v in kw.items():
            if not v or k == 'portal_status_message':
                pass
            else:
                new_key = self.expand_prefix(k)
                if new_key != k:
                    kw[new_key] = v
                    del kw[k]

        query = kw and ('?%s' % urllib.urlencode(kw)) or ''

        return u'%s%s' % (target, query)

    # interface

    @memoize
    @decode
    def listBatchItems(self):
        batch_obj = self._getBatchObj()

        items = []
        for item in batch_obj:
            item_description = item.Description()
            item_title = item.Title()
            item_type = remote_type = item.Type()
            if item_type == 'Favorite':
                try:
                    item = item.getObject()
                    item_description = item_description or item.Description()
                    item_title = item_title or item.Title()
                    remote_type = item.Type()
                except KeyError:
                    pass
            is_file = remote_type in ('File', 'Image')
            is_link = remote_type == 'Link'
            items.append({'description': item_description,
                          'format': is_file and item.Format() or '',
                          'icon': item.getIconURL(),
                          'size': is_file and ('%0.0f kb' %
                                            (item.get_size() / 1024.0)) or '',
                          'title': item_title,
                          'type': item_type,
                          'url': is_link and item.getRemoteUrl() or
                                 item.absolute_url()})
        return tuple(items)

    @memoize
    def navigation_previous(self):
        batch_obj = self._getBatchObj().previous
        if batch_obj is None:
            return

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Previous item')
        else:
            title = _(u'Previous ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def navigation_next(self):
        batch_obj = self._getBatchObj().next
        if batch_obj is None:
            return

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Next item')
        else:
            title = _(u'Next ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    def page_range(self):
        """Create a range of up to ten pages around the current page"""
        b_size = self._BATCH_SIZE
        range_start = max(self.page_number() - 5, 0)
        range_stop = min(max(self.page_number() + 5, 10), self.page_count())

        pages = []
        for p in range(range_start, range_stop):
            b_start = p * b_size
            pages.append({'number': p + 1,
                          'url': self._getNavigationURL(b_start)})
        return pages

    @memoize
    def page_count(self):
        """Count total number of pages in the batch"""
        batch_obj = self._getBatchObj()
        count = (batch_obj.sequence_length - 1) / self._BATCH_SIZE + 1
        return count

    @memoize
    def page_number(self):
        """Get the number of the current page in the batch"""
        return (self._getBatchStart() / self._BATCH_SIZE) + 1

    @memoize
    def summary_length(self):
        length = self._getBatchObj().sequence_length
        if sys.version_info < (2, 7):
            # BBB: for Python 2.6
            return length and thousands_commas(length) or ''
        return length and '{:,}'.format(length) or ''

    @memoize
    def summary_type(self):
        length = self._getBatchObj().sequence_length
        return (length == 1) and _(u'item') or _(u'items')

    @memoize
    @decode
    def summary_match(self):
        return self.request.form.get('SearchableText')


class ContentProxy(object):
    """Utility wrapping content item for display purposes"""

    def __init__(self, context):
        self.name = context.getId()
        self.title = context.Title() or context.getId()
        self.type = context.Type() or None
        self.icon = context.icon
        self.url = context.absolute_url()
        self.ModificationDate = context.ModificationDate()


class ContentsView(BatchViewBase, _EditFormMixin, form.PageForm):
    """Folder contents view"""

    template = ViewPageTemplateFile('folder_contents.pt')
    prefix = 'form'

    object_actions = form.Actions(
        form.Action(
            name='rename',
            label=_(u'Rename'),
            validator='validate_items',
            condition='show_rename',
            success='handle_rename',
            failure='handle_failure'),
        form.Action(
            name='cut',
            label=_(u'Cut'),
            condition='show_basic',
            validator='validate_items',
            success='handle_cut',
            failure='handle_failure'),
        form.Action(
            name='copy',
            label=_(u'Copy'),
            condition='show_basic',
            validator='validate_items',
            success='handle_copy',
            failure='handle_failure'),
        form.Action(
            name='paste',
            label=_(u'Paste'),
            condition='show_paste',
            success='handle_paste'),
        form.Action(
            name='delete',
            label=_(u'Delete'),
            condition='show_delete',
            validator='validate_items',
            success='handle_delete',
            failure='handle_failure')
            )

    delta_actions = form.Actions(
        form.Action(
            name='up',
            label=_(u'Up'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_up',
            failure='handle_failure'),
        form.Action(
            name='down',
            label=_(u'Down'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_down',
            failure='handle_failure')
            )

    absolute_actions = form.Actions(
        form.Action(
            name='top',
            label=_(u'Top'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_top',
            failure='handle_failure'),
        form.Action(
            name='bottom',
            label=_(u'Bottom'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_bottom',
            failure='handle_failure')
            )

    sort_actions = form.Actions(
        form.Action(
            name='sort_order',
            label=_(u'Set as Default Sort'),
            condition='can_sort_be_changed',
            success='handle_sort_order',
            failure='handle_failure')
            )

    actions = object_actions + delta_actions + absolute_actions + sort_actions
    form_fields = form.FormFields()
    delta_field = form.FormFields(IDeltaItem)
    description = u''

    @property
    def label(self):
        return _(u'Folder Contents: ${obj_title}',
                 mapping={'obj_title': self.title()})

    def content_fields(self):
        """Create content field objects only for batched items"""
        show_widgets = self._checkPermission(ViewManagementScreens)
        f = IFolderItem['select']
        contents = []
        b_start = self._getBatchStart()
        key, _reverse = self._get_sorting()
        fields = form.FormFields()
        for idx, item in enumerate(self._getBatchObj()):
            field = form.FormField(f, 'select', item.id)
            fields += form.FormFields(field)
            content = ContentProxy(item)
            if show_widgets:
                content.widget = '{0}.select'.format(content.name)
            else:
                content.widget = None
            if key == 'position':
                content.position = b_start + idx + 1
            else:
                content.position = '...'
            contents.append(content)
        self.listBatchItems = contents
        return fields

    @memoize
    @decode
    def up_info(self):
        """Link to the contens view of the parent object"""
        up_obj = self.context.aq_inner.aq_parent
        mtool = getUtility(IMembershipTool)
        allowed = mtool.checkPermission(ListFolderContents, up_obj)
        if allowed:
            if IDynamicType.providedBy(up_obj):
                up_url = up_obj.getActionInfo('object/folderContents')['url']
                return {'icon': '%s/UpFolder_icon.gif' % self._getPortalURL(),
                        'id': up_obj.getId(),
                        'url': up_url}
            else:
                return {'icon': '',
                        'id': 'Root',
                        'url': ''}
        else:
            return {}

    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the folder contents."""
        super(ContentsView, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(
                self.content_fields(), self.prefix, self.context,
                self.request, ignore_request=ignore_request)
        self.widgets += form.setUpWidgets(
                self.delta_field, self.prefix, self.context,
                self.request, ignore_request=ignore_request)

    @memoize
    def _get_sorting(self):
        """How should the contents be sorted"""
        data = self._getHiddenVars()
        key = data.get('sort_key')
        if key:
            return (key, data.get('reverse', 0))
        else:
            return self.context.getDefaultSorting()

    @memoize
    def column_headings(self):
        key, reverse = self._get_sorting()
        columns = ({'sort_key': 'Type',
                    'title': _(u'Type'),
                    'colspan': '2'},
                   {'sort_key': 'getId',
                    'title': _(u'Name')},
                   {'sort_key': 'modified',
                    'title': _(u'Last Modified')},
                   {'sort_key': 'position',
                    'title': _(u'Position')})
        for column in columns:
            paras = {'form.sort_key': column['sort_key']}
            if key == column['sort_key'] \
            and not reverse and key != 'position':
                paras['form.reverse'] = 1
            query = urllib.urlencode(paras)
            column['url'] = '%s?%s' % (self._getViewURL(), query)
        return tuple(columns)

    @memoize
    def _get_items(self):
        key, reverse = self._get_sorting()
        items = self.context.contentValues()
        return sort(items, ((key, 'cmp', reverse and 'desc' or 'asc'),))

    def _get_ids(self, data):
        """Identify objects that have been selected"""
        ids = [k[:-7] for k, v in data.items()
                 if v is True and k.endswith('.select')]
        return ids

    #Action conditions
    @memoize
    def show_basic(self, action=None):
        if not self._checkPermission(ViewManagementScreens):
            return False
        return bool(self._get_items())

    @memoize
    def show_delete(self, action=None):
        if not self.show_basic():
            return False
        return self._checkPermission(DeleteObjects)

    @memoize
    def show_paste(self, action=None):
        """Any data in the clipboard"""
        if not self._checkPermission(ViewManagementScreens):
            return False
        if not self._checkPermission(AddPortalContent):
            return False
        return bool(self.context.cb_dataValid())

    @memoize
    def show_rename(self, action=None):
        if not self.show_basic():
            return False
        if not self._checkPermission(AddPortalContent):
            return False
        return self.context.allowedContentTypes()

    @memoize
    def can_sort_be_changed(self, action=None):
        """Returns true if the default sort key may be changed
            may be sorted for display"""
        if not self._checkPermission(ViewManagementScreens):
            return False
        if not self._checkPermission(ManageProperties):
            return False
        return not self._get_sorting() == self.context.getDefaultSorting()

    @memoize
    def is_orderable(self, action=None):
        """Returns true if the displayed contents can be
            reorded."""
        if not self._checkPermission(ViewManagementScreens):
            return False
        if not self._checkPermission(ManageProperties):
            return False
        key, _reverse = self._get_sorting()
        return key == 'position' and len(self._get_items()) > 1

    #Action validators
    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for
        the requested action."""
        errors = self.validate(action, data)
        if errors:
            return errors
        if self._get_ids(data) == []:
            errors.append(_(u"Please select one or more items first."))
        return errors

    #Action handlers
    def handle_rename(self, action, data):
        """Redirect to rename view passing the ids of objects to be renamed"""
        # currently redirects to a PythonScript
        # should be replaced with a dedicated form
        self.request.form['ids'] = self._get_ids(data)
        keys = ",".join(self._getHiddenVars().keys() + ['ids'])
        # keys = 'b_start, ids, key, reverse'
        return self._setRedirect('portal_types', 'object/rename_items', keys)

    def handle_cut(self, action, data):
        """Cut the selected objects and put them in the clipboard"""
        ids = self._get_ids(data)
        try:
            self.context.manage_cutObjects(ids, self.request)
            if len(ids) == 1:
                self.status = _(u'Item cut.')
            else:
                self.status = _(u'Items cut.')
        except CopyError:
            self.status = _(u'CopyError: Cut failed.')
        except zExceptions_Unauthorized:
            self.status = _(u'Unauthorized: Cut failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_copy(self, action, data):
        """Copy the selected objects to the clipboard"""
        ids = self._get_ids(data)
        try:
            self.context.manage_copyObjects(ids, self.request)
            if len(ids) == 1:
                self.status = _(u'Item copied.')
            else:
                self.status = _(u'Items copied.')
        except CopyError:
            self.status = _(u'CopyError: Copy failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_paste(self, action, data):
        """Paste the objects from the clipboard into the folder"""
        try:
            result = self.context.manage_pasteObjects(self.request['__cp'])
            if len(result) == 1:
                self.status = _(u'Item pasted.')
            else:
                self.status = _(u'Items pasted.')
        except CopyError:
            self.status = _(u'CopyError: Paste failed.')
            self.request['RESPONSE'].expireCookie('__cp',
                    path='%s' % (self.request['BASEPATH1'] or "/"))

        except zExceptions_Unauthorized:
            self.status = _(u'Unauthorized: Paste failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_delete(self, action, data):
        """Delete the selected objects"""
        ids = self._get_ids(data)
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            self.status = _(u'Item deleted.')
        else:
            self.status = _(u'Items deleted.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_up(self, action, data):
        """Move the selected objects up the selected number of places"""
        ids = self._get_ids(data)
        delta = data.get('delta', 1)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsUp(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved up.')
            elif attempt > 1:
                self.status = _(u'Items moved up.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_down(self, action, data):
        """Move the selected objects down the selected number of places"""
        ids = self._get_ids(data)
        delta = data.get('delta', 1)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsDown(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved down.')
            elif attempt > 1:
                self.status = _(u'Items moved down.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_top(self, action, data):
        """Move the selected objects to the top of the page"""
        ids = self._get_ids(data)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsToTop(ids,
                                                    subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved to top.')
            elif attempt > 1:
                self.status = _(u'Items moved to top.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_bottom(self, action, data):
        """Move the selected objects to the bottom of the page"""
        ids = self._get_ids(data)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsToBottom(ids,
                                                       subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved to bottom.')
            elif attempt > 1:
                self.status = _(u'Items moved to bottom.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/folderContents')

    def handle_sort_order(self, action, data):
        """Set the sort options for the folder."""
        self.context.setDefaultSorting(*self._get_sorting())
        self.status = _(u'Default sort order changed.')
        return self._setRedirect('portal_types', 'object/folderContents')


class FolderView(BatchViewBase):

    """View for IFolderish.
    """

    @memoize
    def _get_items(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.context.contentValues()
        items = sort(items, ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return LazyFilter(items, skip='View')

    @memoize
    def has_local(self):
        return 'local_pt' in self.context.objectIds()
