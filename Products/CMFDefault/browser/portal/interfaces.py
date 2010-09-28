"""Schema for portal forms"""
import codecs

from zope.interface import Interface
from zope.schema import TextLine, ASCIILine, Bool, Choice
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFDefault.utils import Message as _

email_policy = SimpleVocabulary.fromItems(
         [
         (_(u"Generate and email members' initial password"), True),
         (_(u"Allow members to select their initial password"), False)
         ]
         )

def check_encoding(value):
    encoding = ""
    try:
        encoding = codecs.lookup(value)
    except LookupError:
        pass
    return encoding != ""

class IPortalConfig(Interface):
    
    email_from_name = TextLine(
                        title=_(u"Portal 'From' name"),
                        description=_(u"When the portal generates mail, it uses this name as its (apparent) sender."),
                        required=False)
                        
    email_from_address = TextLine(
                        title=_(u"Portal 'From' address"),
                        description=_(u"When the portal generates mail, it uses this address as its (apparent) return address."),
                        required=False)

    smtp_server = TextLine(
                        title=_(u"SMTP server"),
                        description=_(u"This is the address of your local SMTP (out-going mail) server."),
                        required=False)
                        
    title = TextLine(
                    title=_(u"Portal title"),
                    description=_(u"This is the title which appears at the top of every portal page."),
                    required=False)
                    
    description = TextLine(
                    title=_(u"Portal description"),
                    description=_(u"This description is made available via syndicated content and elsewhere. It should be fairly brief"),
                    required=False)
                    
    validate_email = Choice(
                    title=_(u"Password policy"),
                    vocabulary=email_policy,
                    default=False,
                    )

    default_charset = ASCIILine(
                    title=_(u"Portal default encoding"),
                    description=_(u"Charset used to decode portal content strings. If empty, 'utf-8' is used."),
                    required=False,
                    constraint=check_encoding,
                    default="UTF-8")
                    
    email_charset = ASCIILine(
                    title=_(u"Portal email encoding"),
                    description=_(u"Charset used to encode emails send by the portal. If empty, 'utf-8' is used if necessary."),
                    required=False,
                    constraint=check_encoding,
                    default="UTF-8")
    
    enable_actionicons = Bool(
                    title=_(u"Action icons"),
                    description=_(u"Actions available to the user are shown as                    textual links. With this option enabled, they are also shown as icons if the action definition specifies one."),
                    required=False)
                    
    enable_permalink = Bool(
                    title=_(u"Permalink"),
                    description=_(u"If permalinks are enabled then a unique identifier is assigned to every item of content independent of it's id or position in a site. This requires the CMFUid tool to be installed."),
                    required=False)