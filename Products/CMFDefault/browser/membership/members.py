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

from Products.CMFDefault.browser.utils import memoize
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


class MemberProxy(object):
    """Utility class wrapping a member"""
    
    def __init__(self, member):
        self.context = member
        
    def get(self, property):
        return self.context.getProperty(property)

    @property
    def login_time(self):
        login_time = self.get('login_time')
        return login_time == '2000/01/01' and '---' or login_time.Date()
        
    @property
    def name(self):
        return self.context.getId()
        
    @property
    def home(self):
        return self.get('getHomeUrl')
        
    @property
    def email(self):
        return self.get('email')
        
    @property
    def widget(self):
        return "%s.select" % self.name


class Manage(BatchViewBase, EditFormBase):
    
    label = _(u"Manage Members")
    template = ViewPageTemplateFile("members.pt")
    delete_template = ViewPageTemplateFile("delete_members.pt")
    form_fields = form.FormFields()
    hidden_fields = form.FormFields(IBatchForm)
    errors = ()
    
    manage_actions = form.Actions(
        form.Action(
            name='new',
            label=_(u'New...'),
            success='handle_add',
            failure='handle_failure'),
        form.Action(
            name='select',
            label=_(u'Delete...'),
            success='handle_select_for_deletion',
            validator=('validate_items')
                )
            )
            
    delete_actions = form.Actions(
        form.Action(
            name='delete',
            label=_(u'Delete'),
            success='handle_delete',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel'),
                )
            )
    actions = manage_actions + delete_actions

    def _get_items(self):
        mtool = self._getTool('portal_membership')
        return mtool.listMembers()

    def _get_ids(self, data):
        """Identify objects that have been selected"""
        ids = [k.split(".select")[0] for k, v in data.items()
                 if v is True]
        return ids
        
    def member_fields(self):
        """Create content field objects only for batched items
        Also create pseudo-widget for each item
        """
        f = IMemberItem['select']
        members = []
        fields = form.FormFields()
        for item in self._getBatchObj():
            field = form.FormField(f, 'select', item.id)
            fields += form.FormFields(field)
            members.append(MemberProxy(item))
        self.listBatchItems = members
        return fields
        
    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the members"""
        super(Manage, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(self.member_fields(), self.prefix,
                    self.context, self.request, ignore_request=ignore_request)

    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for
        the requested action."""
        super(Manage, self).validate(action, data)
        if data is None or data == {}:
            return [_(u"Please select one or more items first.")]
        else:
            return []

    def handle_add(self, action, data):
        """Redirect to the join form where managers can add users"""
        return self._setRedirect('portal_actions', 'user/join')
        
    def handle_select_for_deletion(self, action, data):
        """Identify members to be deleted and redirect to confirmation
        template"""
        self.status = ", ".join(self._get_ids(data))
        return self.delete_template()
        
    def handle_delete(self, action, data):
        """Delete selected members"""
        mtool = self._getTool('portal_membership')
        mtool.deleteMembers(self._get_ids(data))
        return self.request.response.redirect(self.request.URL)
