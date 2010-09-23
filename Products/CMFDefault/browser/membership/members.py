"""
Forms for managing members
"""
from logging import getLogger

LOG = getLogger("Manage Members Form")

from zope.interface import Interface
from zope.formlib import form
from zope.schema import Bool, TextLine, Date, getFieldsInOrder, List, Choice

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.utils import Message as _

from Products.CMFDefault.browser.content.folder import BatchViewBase
from Products.CMFDefault.browser.content.interfaces import IBatchForm

class IMemberItem(Interface):
    """Schema for portal members """

    select = Bool(
        required=False)

    name = TextLine(
        title=u"Name",
        required=False,
        readonly=True
        )
        
    email = TextLine(
        title=_(u"E-mail Address"),
        required=False,
        readonly=True
        )
        
    last_login = Date(
        title=_(u"Last Login"),
        required=False,
        readonly=True
        )


class Manage(BatchViewBase, EditFormBase):
    
    label = _(u"Manage Members")
    template = ViewPageTemplateFile("members.pt")
    delete_template = ViewPageTemplateFile("delete_members.pt")
    members_selected = False
    
    actions = form.Actions(
        form.Action(
            name='new',
            label=_(u'New...'),
            success='handle_add',
            failure='handle_failure'),
        form.Action(
            name='select',
            label=_(u'Delete...'),
            condition="no_members_selected",
            validator='validate_items',
            success='handle_select_for_deletion'
                ),
        form.Action(
            name='delete',
            label=_(u'Delete'),
            # condition="members_are_selected",
            success='handle_delete',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel'),
            condition="members_are_selected",
                )
            )
            
    hidden_fields = form.FormFields(IBatchForm)
    
    def _get_items(self):
        mtool = self._getTool('portal_membership')
        return mtool.listMembers()
        
    def form_fields(self):
        """Create content field objects only for batched items"""
        fields = form.FormFields()
        for item in self._getBatchObj():
            for name, field in getFieldsInOrder(IMemberItem):
                field = form.FormField(field, name, item.id)
                fields += form.FormFields(field)
        return fields
        
    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the members"""
        super(Manage, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(self.form_fields(), self.prefix,
                    self.context, self.request, ignore_request=ignore_request)
                
    def no_members_selected(self, action=None):
        return not self.members_selected
        
    def members_are_selected(self, action=None):
        return self.members_selected

    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for
        the requested action."""
        super(Manage, self).validate(action, data)
        if data is None or data == {}:
            return [_(u"Please select one or more items first.")]
        else:
            return []
            
    def selected(self, data):
        """Return the id of the selected objects"""
        return (key.split(".")[0] for key, value in data.items()
                                  if value is True)

    def handle_add(self, action, data):
        """Redirect to the join form where managers can add users"""
        return self._setRedirect('portal_actions', 'user/join')
        
    def handle_select_for_deletion(self, action, data):
        """Identify members to be deleted and redirect to confirmation
        template"""
        self.status = ", ".join(self.selected(data))
        return self.delete_template()
        
    def handle_delete(self, action, data):
        mtool = self._getTool('portal_membership')
        mtool.deleteMembers(self.selected(data))
        self.members_selected = False
        return self.request.response.redirect(self.request.URL)
    