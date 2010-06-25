"""CSS for action icons
$Id$
"""
from logging import getLogger

LOG = getLogger("Action Icons CSS")

from zope.component import getUtility

from Products.Five.browser import BrowserView

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.browser.utils import memoize

class View(BrowserView):
    
    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.show_icons = self._show_icons

    @property
    @memoize
    def _show_icons(self):
        """Are action icons enabled?"""
        ptool = getUtility(IPropertiesTool)
        show = ptool.getProperty('enable_actionicons')
        if show:
            self.icon = ".icon {padding-left: 1.5em;}\n\n"
        else:
            self.icon = ".icon {padding-left: 0.5em;}\n\n"
        return show

    @property
    @memoize
    def template(self):
        """Always return a template so there are no browser errors"""
        if self.show_icons:    
            return ".%s {background: url(%s) no-repeat 0.1em}"
        else:
            return ".%s {/* %s */}"

    @memoize
    def actions(self):
        """List all action icons"""
        atool = getToolByName(self.context, 'portal_actions')
        all_actions = atool.listFilteredActionsFor(self.context)
        icons = []
        for cat in ['user', 'object', 'folder', 'workflow', 'global']:
            cat_actions = all_actions[cat]
            icons.append("/* %s actions */" % cat)
            for a in cat_actions:
                icons.append(self.template % (a['id'], a['icon']))
        return "\n\n".join(icons)

    @memoize
    def types(self):
        """List all type icons"""
        ttool = getToolByName(self.context, 'portal_types')
        types = ttool.listTypeInfo()
        econtext = getExprContext(self.context)
        icons = [self.template %  (t.id,
                                  t.getIconExprObject()(econtext)) \
                for t in types]
        return "\n\n".join(icons)

    def __call__(self):
        self.request.response.setHeader("content-type", "text/css")
        self.request.response.write(self.icon)
        self.request.response.write(self.actions())
        self.request.response.write(self.types())
