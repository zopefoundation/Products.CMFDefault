##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Workflow history view"""

from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import ViewBase
from Products.CMFDefault.browser.utils import memoize, decode


class View(ViewBase):

    @property
    @memoize
    def workflow(self):
        return self._getTool('portal_workflow')

    @decode
    @memoize
    def review_state(self):
        return self.workflow.getInfoFor(self.context, 'review_state')

    @decode
    @memoize
    def review_history(self):
        history = self.workflow.getInfoFor(self.context, 'review_history')
        if not history:
            return
        return reversed(history)
