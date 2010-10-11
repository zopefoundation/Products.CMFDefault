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
"""Search form tests"""

import unittest

from Products.CMFCore.tests.base.dummy import DummySite, DummyTool
from Products.CMFDefault.browser.test_utils import DummyRequest, DummyResponse


class SearchFormTests(unittest.TestCase):

    def setUp(self):
        self.site = site = DummySite('site')
        site._setObject('portal_membership', DummyTool())

    def _getTargetClass(self):
        from Products.CMFDefault.browser.search.search import Search
        return Search(self.site, DummyRequest())

    def test_is_anonymous(self):
        view = self._getTargetClass()
        self.assertTrue(view.is_anonymous)
        self.assertEqual(view.search_fields.get('review_state'), None)

    def test_is_not_anonymous(self):
        view = self._getTargetClass()
        self.site.portal_membership.anon = 0
        self.assertFalse(view.is_anonymous)
        self.assertNotEqual(view.search_fields.get('review_state'), None)

    def test_add_search_vars_to_hidden(self):
        view = self._getTargetClass()
        self.assertEqual(view._query, {})
        data = {'portal_type': ['Document']}
        view.handle_search('search', data)
        self.assertEqual(view._query, data)

    def test_search_returns_results(self):
        view = self._getTargetClass()
        self.assertNotEqual(view.template, view.results)
        view.handle_search('search', {})
        self.assertEqual(view.template.filename, view.results.filename)

    def results(self):
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SearchFormTests))
    return suite
