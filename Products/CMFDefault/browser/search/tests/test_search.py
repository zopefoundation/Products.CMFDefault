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

from zope.component import getSiteManager
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFDefault.browser.test_utils import DummyRequest


class SearchFormTests(unittest.TestCase):

    def setUp(self):
        self.site = DummySite('site')
        getSiteManager().registerUtility(DummyTool(), IMembershipTool)

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from Products.CMFDefault.browser.search.search import Search
        return Search(self.site, DummyRequest())

    def test_is_anonymous(self):
        view = self._getTargetClass()
        self.assertTrue(view.is_anonymous)
        self.assertEqual(view.search_fields.get('review_state'), None)

    def test_is_not_anonymous(self):
        view = self._getTargetClass()
        getSiteManager().getUtility(IMembershipTool).anon = 0
        self.assertFalse(view.is_anonymous)
        self.assertNotEqual(view.search_fields.get('review_state'), None)

    def test_strip_unused_paramaters(self):
        view = self._getTargetClass()
        data = {'portal_type': ['Document'], 'review_state': u"None",
                'Subject': u"None"}
        view.handle_search('search', data)
        self.assertEqual(view._query, {'portal_type': ['Document']})

    def test_add_search_vars_to_hidden(self):
        view = self._getTargetClass()
        self.assertFalse(hasattr(view, '_query'))
        data = {'portal_type': ['Document']}
        view.handle_search('search', data)
        self.assertEqual(view._getNavigationVars(), data)

    def test_search_returns_results(self):
        view = self._getTargetClass()
        self.assertNotEqual(view.template, view.results)
        view.handle_search('search', {})
        self.assertEqual(view.template.filename, view.results.filename)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SearchFormTests))
    return suite
