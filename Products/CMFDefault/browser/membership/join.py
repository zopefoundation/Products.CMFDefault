"""
Join form
$Id$
"""

from zope.formlib import form
from zope.interface import Interface
from zope.schema import ASCIILine, Password, Bool

from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine

from Products.CMFDefault.utils import Message as _

class IZopeChooseSchema(Interface):
    """Zope generates password and sends it by e-mail"""
    
    member_id = ASCIILine(
                    title=_(u"Member ID")
                    )
                    
    email = EmailLine(
                    title=_(u"E-mail address")
                    )
    
class IUserChooseSchema(IZopeChooseSchema):
    """User is allowed to set their own e-mail"""
    
    password = Password(
                    title=_(u"Password")
                    )
                    
    password_confirmation = Password(
                    title=_(u"Password (confirm)")
                    )
                    
    send_password = Bool(
                    title=_(u"Mail Password?"),
                    description=_(u"Check this box to have the password mailed."))


class Join(EditFormBase):
    
    actions = form.Actions(
        form.Action(
            name='register',
            label=_(u'Register'),
            validator='handle_register_validate',
            success='handle_success',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel')
                )
            )
    
    def __init__(self, context, request):
        super(Join, self).__init__(context, request)
        ptool = self._getTool("portal_properties")
        validate = ptool.getProperty('validate_email')
        if validate:
            self.form_fields = form.FormFields(IZopeChooseSchema)
        else:
            self.form_fields = form.FormFields(IUserChooseSchema)
            
    def add_member(self, data):
        """add member"""
        
    def send_password(self):
        """send password"""
        
    def handle_success(self, action, data):
        """"""

    def handle_failure(self, action, data):
        pass
