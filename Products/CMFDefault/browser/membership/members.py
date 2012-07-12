##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Forms for managing members.
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.formlib import form
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Date
from zope.schema import TextLine
from zope.sequencesort.ssort import sort
from ZTUtils import LazyFilter

from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.widgets.batch import BatchViewBase
from Products.CMFDefault.browser.widgets.batch import IBatchForm
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _


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
        title=_(u"Email Address"),
        required=False,
        readonly=True
        )

    last_login = Date(
        title=_(u"Last Login"),
        required=False,
        readonly=True
        )


class MemberProxy(object):

    """Utility class wrapping a member for display purposes"""

    def __init__(self, member, mtool):
        member_id = member.getId()
        fullname = member.getProperty('fullname')
        last_login = member.getProperty('login_time')
        never_logged_in = str(last_login).startswith('2000/01/01')
        self.login_time = never_logged_in and '---' or last_login.Date()
        self.name = '%s (%s)' % (fullname, member_id)
        self.home = mtool.getHomeUrl(member_id, verifyPermission=0)
        self.email = member.getProperty('email')
        self.widget = "%s.select" % member_id


class Manage(BatchViewBase, EditFormBase):

    template = ViewPageTemplateFile("members.pt")
    delete_template = ViewPageTemplateFile("members_delete.pt")
    guillotine = None
    prefix = 'form' # required for hidden fields to work
    form_fields = form.FormFields()
    hidden_fields = form.FormFields(IBatchForm)

    manage_actions = form.Actions(
        form.Action(
            name='new',
            label=_(u'New...'),
            success='handle_add',
            failure='handle_failure'),
        form.Action(
            name='select',
            label=_(u'Delete...'),
            condition='members_exist',
            success='handle_select_for_deletion',
            failure='handle_failure',
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
            success='handle_cancel'
                )
            )
    actions = manage_actions + delete_actions
    label = _(u'Manage Members')

    @property
    def description(self):
        if not self.members_exist():
            return _(u'Currently there are no members registered.')
        return u''

    @memoize
    def _get_items(self):
        mtool = getUtility(IMembershipTool)
        return mtool.listMembers()

    @memoize
    def members_exist(self, action=None):
        return len(self._getBatchObj()) > 0

    def _get_ids(self, data):
        """Identify objects that have been selected"""
        ids = [k[:-7] for k, v in data.items()
                 if v is True and k.endswith('.select')]
        return ids

    @memoize
    def member_fields(self):
        """Create content field objects only for batched items
        Also create pseudo-widget for each item
        """
        mtool = getUtility(IMembershipTool)
        f = IMemberItem['select']
        members = []
        fields = form.FormFields()
        for item in self._getBatchObj():
            field = form.FormField(f, 'select', item.getId())
            fields += form.FormFields(field)
            members.append(MemberProxy(item, mtool))
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
        errors = self.validate(action, data)
        if errors:
            return errors
        if self._get_ids(data) == []:
            errors.append(_(u"Please select one or more members first."))
        return errors

    def handle_add(self, action, data):
        """Redirect to the join form where managers can add users"""
        return self._setRedirect('portal_actions', 'global/members_register')

    def handle_select_for_deletion(self, action, data):
        """Identify members to be deleted and redirect to confirmation
        template"""
        mtool = getUtility(IMembershipTool)
        charset = self._getDefaultCharset()
        members = []
        for member_id in self._get_ids(data):
            member = mtool.getMemberById(member_id)
            fullname = member.getProperty('fullname').decode(charset)
            members.append(u'{0} ({1})'.format(fullname, member_id))
        self.guillotine = u', '.join(members)
        return self.delete_template()

    def handle_delete(self, action, data):
        """Delete selected members"""
        mtool = getUtility(IMembershipTool)
        mtool.deleteMembers(self._get_ids(data))
        self.status = _(u"Selected members deleted.")
        self._setRedirect('portal_actions', "global/manage_members",
                          '{0}.b_start'.format(self.prefix))

    def handle_cancel(self, action, data):
        """Don't delete anyone, return to list"""
        self.status = _(u"Deletion broken off.")
        self._setRedirect('portal_actions', "global/manage_members",
                          '{0}.b_start'.format(self.prefix))


class Roster(BatchViewBase):

    hidden_fields = form.FormFields(IBatchForm)
    form_fields = form.FormFields()
    actions = ()
    template = ViewPageTemplateFile("members_list.pt")

    @property
    @memoize
    def mtool(self):
        return getUtility(IMembershipTool)

    @memoize
    def isUserManager(self):
        return self.mtool.checkPermission('Manage users',
                          self.mtool.getMembersFolder()
                                            )

    @memoize
    def _get_items(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.mtool().getRoster()
        items = sort(items, ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return LazyFilter(items, skip='View')

    @memoize
    def listBatchItems(self):
        members = []
        for item in self._getBatchObj():
            member = item
            member['home'] = self.mtool().getHomeUrl(item['id'],
                                verifyPermission=1)
            member['listed'] = member['listed'] and _(u"Yes") or _("No")
            members.append(member)
        return members
