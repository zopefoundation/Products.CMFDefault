from zope.component import getUtility
from zope.interface import Interface
from zope.formlib import form
from zope.schema import TextLine, Text

from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _
from Products.PythonScripts.standard import structured_text
from Products.CMFDefault.utils import html_marshal
from Products.CMFDefault.browser.utils import decode, memoize


class IDiscussion(Interface):


    title = TextLine(
        title=_("Title")
    )

    text = Text(
        title=_("Text")
    )


class Discuss(EditFormBase):
    """
    Discuss an item
    """

    form_fields = form.FormFields(IDiscussion)
    actions = form.Actions(
        form.Action(
            name="add",
            label=_("Add"),
            success="handle_add"
            ),
        form.Action(
            name="edit",
            label=_("Edit"),
            success="handle_edit",
            ),
        form.Action(
            name="preview",
            label=_("Preview"),
            success="handle_preview",
            )
    )

    @property
    @memoize
    def atool(self):
        return getUtility(IActionsTool)

    #form = context.REQUEST.form
    #is_preview = False
    #if add and \
            #context.validateHTML(**form) and \
            #context.discussion_reply(**form):
        #return
    #elif preview and \
            #context.validateHTML(**form):
        #is_preview = True


    #options = {}

    #title = form.get('title', context.Title())
    #text = form.get('text', '')
    #options['is_preview'] = is_preview
    #options['title'] = title
    #options['text'] = text
    #options['cooked_text'] = structured_text(text)

    #if is_preview:
        #hidden_vars = [ {'name': n, 'value': v}
                        #for n, v in html_marshal(title=title, text=text) ]
    #else:
        #hidden_vars = []
    #buttons = []
    #target = atool.getActionInfo('object/reply', context)['url']
    #buttons.append( {'name': 'add', 'value': _(u'Add')} )
    #if is_preview:
        #buttons.append( {'name': 'edit', 'value': _(u'Edit')} )
    #else:
        #buttons.append( {'name': 'preview', 'value': _(u'Preview')} )
    #options['form'] = { 'action': target,
                        #'listHiddenVarInfos': tuple(hidden_vars),
                        #'listButtonInfos': tuple(buttons) }

    #return context.discussion_reply_template(**decode(options, script))



class Delete(EditFormBase):
    """
    Delete an item from a discussion
    """

    @property
    @memoize
    def dtool(self):
        return getUtility(IDiscussionTool)

    def __call__(self):
        parent = self.context.inReplyTo()
        talkback = self.dtool.getDiscussionFor(parent)
        talkback.deleteReply(self.context.getId())

    def setRedirect(self):
        self.context.setStatus(True, _(u'Reply deleted.'))
        self.context.setRedirect(parent, 'object/view')
