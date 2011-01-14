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
"""RSS view for syndicatable items"""

from ZTUtils import LazyFilter

from zope.component import getAdapter
from zope.sequencesort.ssort import sort

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFDefault.browser.utils import ViewBase, memoize, decode


class View(ViewBase):

    """Return an RSS conform list of content items"""

    @property
    @memoize
    def synd_info(self):
        return getAdapter(self.context, ISyndicationInfo).get_info()

    @memoize
    @decode
    def items(self):
        """Return items according to policy"""

        stool = self._getTool("portal_syndication")
        key, reverse = self.context.getDefaultSorting()
        items = stool.getSyndicatableContent(self.context)
        items = sort(items, ((key, 'cmp', reverse and 'desc' or 'asc'),))
        items = LazyFilter(items, skip='View')
        items = ({'title': o.Title(), 'description': o.Description(),
                  'creators': o.listCreators(), 'subjects': o.Subject(),
                  'rights': o.Rights, 'publisher': o.Publisher(),
                  'url': o.absolute_url(), 'date': o.modified().rfc822(),
                  'uid': None}
                  for idx, o in enumerate(items)
                    if idx < self.synd_info['max_items'])
        return items

    @memoize
    @decode
    def channel(self):
        """Provide infomation about the channel"""
        converter = {'daily':1, 'weekly':7, 'monthly': 30, 'yearly': 365}
        ttl = 60 * 24 *(self.synd_info['frequency'] *
                            converter[self.synd_info['period']])

        info = {'base': self.synd_info['base'].rfc822(),
                'ttl': ttl,
                'period': self.synd_info['period'],
                'title': self.context.Title(),
                'description': self.context.Description(),
                'portal_url': self._getTool('portal_url')()
                }
        return info