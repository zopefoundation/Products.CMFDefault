import urllib

from DocumentTemplate import sequence

from zope.interface import Interface, directlyProvides
from zope import schema
from zope.schema import Bool, TextLine, Int, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.interfaces import IDynamicType

from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.utils import Message as _

from utils import ViewBase
from utils import decode
from utils import memoize

def contents_delta_vocabulary(context):
    """Vocabulary for the pulldown for moving objects up
    and down."""
    length = len(context.contentIds())
    deltas = [SimpleTerm(str(i), str(i), str(i)) 
            for i in range(1, min(5, length)) + range(5, length, 5)]
    return SimpleVocabulary(deltas)

class IFolderItem(Interface):
    """Schema for folderish objects contents."""
    
    select = Bool(
        required=False)
        
    name = TextLine(
        title=u"Name",
        required=False,
        readonly=True)

class IDeltaItem(Interface):
    """Schema for delta"""    
    delta = Choice(
        title=u"By",
        description=u"Move an object up or down the chosen number of places.",
        required=False,
        vocabulary=u'cmf.contents delta vocabulary',
        default=u'1')
        

class ContentsView(ContentEditFormBase):
    """Folder contents view"""
    
    template = ViewPageTemplateFile('templates/contents.pt')
    
    object_actions = form.Actions(
        form.Action(
            name='rename',
            label=_(u'Rename'),
            validator='validate_items',
            condition='has_subobjects',
            success='handle_rename'),
        form.Action(
            name='cut',
            label=_(u'Cut'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_cut'),
        form.Action(
            name='copy',
            label=_(u'Copy'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_copy'),
        form.Action(
            name='paste',
            label=_(u'Paste'),
            condition='check_clipboard_data',
            success='handle_paste'),
        form.Action(
            name='delete',
            label=_(u'Delete'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_delete')
            )
            
    delta_actions = form.Actions(
        form.Action(
            name='up',
            label=_(u'Up'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_up'),
        form.Action(
            name='down',
            label=_(u'Down'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_down')
            )
            
    absolute_actions = form.Actions(
        form.Action(
            name='top',
            label=_(u'Top'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_top'),
        form.Action(
            name='bottom',
            label=_(u'Bottom'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_bottom')
            )

    sort_actions = form.Actions(
        form.Action(
            name='sort_order',
            label=_(u'Set as Default Sort'),
            condition='can_sort_be_changed',
            validator='validate_items',
            success='handle_top')
            )
            
    actions = object_actions + delta_actions + absolute_actions + sort_actions
    
    errors = ()
    
    def __init__(self, *args, **kw):
        super(ContentsView, self).__init__(*args, **kw)
        self.form_fields = form.FormFields()
        self.delta_field = form.FormFields(IDeltaItem)
        self.contents = self.context.contentValues()

        for item in self.contents:
            for n, f in schema.getFieldsInOrder(IFolderItem):
                field = form.FormField(f, n, item.id)
                self.form_fields += form.FormFields(field)
          
    @memoize
    @decode
    def up_info(self):
        """Link to the contens view of the parent object"""
        up_obj = self.context.aq_inner.aq_parent
        mtool = self._getTool('portal_membership')
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
        data = {}
        for i in self.contents:
            data['%s.name' %i.id] = i.getId()
        self.widgets = form.setUpDataWidgets(
                self.form_fields, self.prefix, self.context,
                self.request, data=data, ignore_request=ignore_request)
        self.widgets += form.setUpDataWidgets(self.delta_field, self.prefix,
                        self.context, self.request, ignore_request=ignore_request)
                
    def _get_sorting(self):
        """How should the contents be sorted"""
        key = self.request.form.get('key', None)
        if key:
            return (key, self.request.form.get('reverse', 0))
        else:
            return self.context.getDefaultSorting()
    
    def column_headings(self):
        (key, reverse) = self._get_sorting()
        columns = ( {'key': 'Type',
                     'title': _(u'Type'),
                     'colspan': '2'}
                  , {'key': 'getId',
                     'title': _(u'Name')}
                  , {'key': 'modified',
                     'title': _(u'Last Modified')}
                  , {'key': 'position',
                     'title': _(u'Position')}
                  )
        for column in columns:
            if key == column['key'] and not reverse and key != 'position':
                query = urllib.urlencode({'key':column['key'], 'reverse':1})
            else:
                query = urllib.urlencode({'key':column['key']})
            column['url'] = '%s?%s' % (self._getViewURL(), query)
        return tuple(columns)
        
    def _get_items(self):
        (key, reverse) = self._get_sorting()
        items = self.contents
        return sequence.sort(items,
                             ((key, 'cmp', reverse and 'desc' or 'asc'),))
    
    def layout_fields(self):
        """Return the widgets for the form in the interface field order"""
        fields = []

        for item in self._get_items():
            field = {'ModificationDate':item.ModificationDate()}
            field['select'] = self.widgets['%s.select' % item.getId()]
            field['name'] = self.widgets['%s.name' % item.getId()]
            field['url'] = item.absolute_url()
            field['title'] = item.TitleOrId()
            field['icon'] = item.icon
            field['position'] = self.context.contentIds().index(item.getId()) + 1
            field['type'] = item.Type() or None
            fields.append(field.copy())
        return fields
                
    def _get_ids(self, data):
        """Strip prefixes from ids that have been selected"""
        ids = [k.split(".")[0] for k, v in data.items() if v == True]
        return ids
        
    
    #Action conditions
    @memoize
    def has_subobjects(self, action=None):
        """Return false if the user cannot rename subobjects"""
        return bool(self.contents)
    
    @memoize
    def check_clipboard_data(self, action=None):
        """Any data in the clipboard"""
        return bool(self.context.cb_dataValid())
    
    @memoize
    def can_sort_be_changed(self, action=None):
        """Returns true if the default sort key may be changed 
            may be sorted for display"""
        items_move_allowed = self._checkPermission(ManageProperties)
        return items_move_allowed and not \
            self._get_sorting() == self.context.getDefaultSorting()

    @memoize
    def is_orderable(self, action=None):
        """Returns true if the displayed contents can be
            reorded."""
        (key, reverse) = self._get_sorting()        
        return key == 'position' and len(self.contents) > 1

    #Actions validators
    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for 
        the requested action."""
        if data is None:
            data = {}
        if len(self._get_ids(data)) == 0:
            return [_(u"Please select one or more items first.")]
        else:
            return []
            
    #Action handlers
    def handle_rename(self, action, data):
        """Redirect to rename view passing the ids of objects to be renamed"""
        return self._setRedirect('portal_types', 'object/rename_items')
    
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
        return self._setRedirect('portal_types', 'object/new_contents')
    
    def handle_paste(self, action, data):
        """Paste the objects from the clipboard into the folder"""
        try:
            result = self.context.manage_pasteObjects(self.request['__cp'])
            if len(result) == 1:
                self.status = _(u'Item pasted.')
            else:
                self.status = _(u'Items pasted.')
        except CopyError, error:
            self.status = _(u'CopyError: Paste failed.')
            self.request['RESPONSE'].expireCookie('__cp', 
                    path='%s' % (self.request['BASEPATH1'] or "/"))

        except zExceptions_Unauthorized:
            self.status = _(u'Unauthorized: Paste failed.')
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_delete(self, action, data):
        """Delete the selected objects"""
        ids = self._get_ids(data)
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            self.status = _(u'Item deleted.')
        else:
            self.status = _(u'Items deleted.')
        return self._setRedirect('portal_types', 'object/new_contents')
    
    def handle_up(self, action, data):
        """Move the selected objects up the selected number of places"""
        ids = self._get_ids(data)
        delta = self.request.form.get('delta', 1)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_down(self, action, data):
        """Move the selected objects down the selected number of places"""
        ids = self._get_ids(data)
        delta = self.request.form.get('delta', 1)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/new_contents')
            
    def handle_top(self, action, data):
        """Move the selected objects to the top of the page"""
        ids = self._get_ids(data)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_bottom(self, action, data):
        """Move the selected objects to the bottom of the page"""
        ids = self._get_ids(data)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/new_contents')
        
    def handle_sort_order(self, action, data):
        """Set the sort options for the folder."""
        key = data['position']
        reverse = data.get('reverse', 0)
        self.context.setDefaultSorting(key, reverse)
        self.status = _(u"Sort order changed")
        return self._setRedirect('portal_types', 'object/new_contents')