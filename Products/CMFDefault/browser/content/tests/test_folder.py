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
""" Test Products.CMFDefault.browser.folder
"""

import unittest
from Testing import ZopeTestCase

from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFDefault.browser.content.folder import ContentsView
from Products.CMFDefault.browser.content.folder import FolderView
from Products.CMFDefault.browser.content.tests.utils import clearVocabulary
from Products.CMFDefault.browser.content.tests.utils import setupVocabulary
from Products.CMFDefault.testing import FunctionalLayer


class BatchViewTests(unittest.TestCase):

    def _makeOne(self, batch_size=30):
        from Products.CMFDefault.browser.content.folder import BatchViewBase
        batch = BatchViewBase(None,
                              TestRequest(ACTUAL_URL='http://example.com'))
        batch._get_items = lambda: range(batch_size)
        return batch

    def test_expand_prefix(self):
        batch = self._makeOne()
        self.assertEqual(batch.expand_prefix('key'), 'key')
        batch = self._makeOne()
        batch.prefix= 'form'
        self.assertEqual(batch.expand_prefix('key'), 'form.key')

    def test_page_count(self):
        batch = self._makeOne()
        self.assertEqual(batch.page_count(), 2)
        batch = self._makeOne(25)
        self.assertEqual(batch.page_count(), 1)
        batch = self._makeOne()
        batch._BATCH_SIZE = 2
        self.assertEqual(batch.page_count(), 15)

    def test_page_number(self):
        batch = self._makeOne()
        self.assertEqual(batch.page_number(), 1)
        batch = self._makeOne(1000)
        batch._getBatchStart = lambda: 250
        self.assertEqual(batch.page_number(), 11)

    def test_summary_length(self):
        batch = self._makeOne()
        self.assertEqual(batch.summary_length(), '30')
        batch = self._makeOne(10000)
        self.assertEqual(batch.summary_length(), '10,000')
        batch = self._makeOne(0)
        self.assertEqual(batch.summary_length(), '')

    def test_summary_type(self):
        batch = self._makeOne()
        self.assertEqual(batch.summary_type(), 'items')
        batch = self._makeOne()
        batch._get_items = lambda: range(1)
        self.assertEqual(batch.summary_type(), 'item')

    def test_navigation_previous(self):
        batch = self._makeOne()
        self.assertEqual(batch.navigation_previous(), None)
        batch = self._makeOne(1000)
        batch._getBatchStart = lambda: 250
        self.assertEqual(batch.navigation_previous(),
                         {'url': u'http://example.com?b_start=225',
                          'title': u'Previous ${count} items'}
                         )

    def test_navigation_next(self):
        batch = self._makeOne()
        self.assertEqual(batch.navigation_next(),
                         {'url': u'http://example.com?b_start=25',
                          'title': u'Next ${count} items'}
                         )
        batch = self._makeOne(1000)
        batch._getBatchStart = lambda: 250
        self.assertEqual(batch.navigation_next(),
                         {'url': u'http://example.com?b_start=275',
                          'title': u'Next ${count} items'}
                         )

    def test_page_range(self):
        batch = self._makeOne()
        self.assertEqual(batch.page_range(),
                         [{'url': u'http://example.com?b_start=0', 'number': 1},
                          {'url': u'http://example.com?b_start=25', 'number': 2}]
                         )
        batch = self._makeOne(1000)
        self.assertEqual(batch.page_range(),
                         [{'url': u'http://example.com?b_start=0', 'number': 1},
                          {'url': u'http://example.com?b_start=25', 'number': 2},
                          {'url': u'http://example.com?b_start=50', 'number': 3},
                          {'url': u'http://example.com?b_start=75', 'number': 4},
                          {'url': u'http://example.com?b_start=100', 'number': 5},
                          {'url': u'http://example.com?b_start=125', 'number': 6},
                          {'url': u'http://example.com?b_start=150', 'number': 7},
                          {'url': u'http://example.com?b_start=175', 'number': 8},
                          {'url': u'http://example.com?b_start=200', 'number': 9},
                          {'url': u'http://example.com?b_start=225', 'number': 10}]
                         )
        batch = self._makeOne(1000)
        batch._getBatchStart = lambda: 250
        self.assertEqual(batch.page_range(),
                         [{'url': u'http://example.com?b_start=150', 'number': 7},
                          {'url': u'http://example.com?b_start=175', 'number': 8},
                          {'url': u'http://example.com?b_start=200', 'number': 9},
                          {'url': u'http://example.com?b_start=225', 'number': 10},
                          {'url': u'http://example.com?b_start=250', 'number': 11},
                          {'url': u'http://example.com?b_start=275', 'number': 12},
                          {'url': u'http://example.com?b_start=300', 'number': 13},
                          {'url': u'http://example.com?b_start=325', 'number': 14},
                          {'url': u'http://example.com?b_start=350', 'number': 15},
                          {'url': u'http://example.com?b_start=375', 'number': 16}]
                         )


class FolderContentsViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        self.site = site = DummySite('site')
        sm = getSiteManager()
        sm.registerUtility(DummyTool(), IMembershipTool)
        sm.registerUtility(DummyTool().__of__(site), IPropertiesTool)
        sm.registerUtility(DummyTool().__of__(site), IURLTool)
        sm.registerUtility(DummyTool(), ITypesTool)
        folder = PortalFolder('test_folder')
        self.folder = site._setObject('test_folder', folder)

    def tearDown(self):
        cleanUp()

    def _make_one(self, name="DummyItem"):
        content = DummyContent(name)
        content.portal_type = "Dummy Content"
        self.folder._setObject(name, content)

    def _make_batch(self):
        """Add enough objects to force pagination"""
        batch_size = ContentsView._BATCH_SIZE
        for i in range(batch_size + 2):
            content_id = "Dummy%s" % i
            self._make_one(content_id)

    def test_getNavigationURL(self):
        url = 'http://example.com/folder_contents'
        self._make_batch()
        view = ContentsView(self.folder, TestRequest(ACTUAL_URL=url))
        self.assertTrue(view._getNavigationURL(25) == url + "?form.b_start=25")

    def test_view(self):
        view = ContentsView(self.folder, TestRequest())
        self.failUnless(IBrowserPublisher.providedBy(view))

    def test_up_info(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals({'url':u'', 'id':u'Root', 'icon':u''},
                            view.up_info())

    def test_list_batch_items(self):
        view = ContentsView(self.folder, TestRequest())
        view.content_fields()
        self.assertEquals(view.listBatchItems, [])

    def test_is_orderable(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.is_orderable())

    def test_sort_can_be_changed(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.can_sort_be_changed())

    def test_empty_has_subobjects(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.has_subobjects())

    def test_has_subobjects(self):
        self._make_one()
        view = ContentsView(self.folder, TestRequest())
        self.failUnless(view.has_subobjects())

    def test_check_clipboard_data(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.check_clipboard_data())

    def test_validate_items(self):
        """Cannot validate forms without widgets"""
        view = ContentsView(self.folder, TestRequest())
        self.assertRaises(AttributeError,
                            view.validate_items, "", {'foo':'bar'})

    def test_get_ids(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals(
                        view._get_ids({'foo':'bar'}),
                        [])
        self.assertEquals(
                        view._get_ids({'DummyItem1.select':True,
                                       'DummyItem2.select':False,
                                       'DummyItem3.select':True}),
                        ['DummyItem1', 'DummyItem3'])
        self.assertEquals(
                        view._get_ids({'delta':True,
                                       'delta':1}),
                        []
                        )


class FolderViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        self.site = site = DummySite('site')
        folder = PortalFolder('test_folder')
        self.folder = site._setObject('test_folder', folder)

    def _make_one(self, name="DummyItem"):
        content = DummyContent(name)
        content.portal_type = "Dummy Content"
        self.folder._setObject(name, content)

    def _make_batch(self):
        """Add enough objects to force pagination"""
        batch_size = ContentsView._BATCH_SIZE
        for i in range(batch_size + 2):
            content_id = "Dummy%s" % i
            self._make_one(content_id)

    def test_getNavigationURL(self):
        url = 'http://example.com/view'
        self._make_batch()
        view = FolderView(self.folder, TestRequest(ACTUAL_URL=url))
        self.assertTrue(view._getNavigationURL(25) == url + "?b_start=25")

    def test_folder_has_local(self):
        self._make_one('local_pt')
        view = FolderView(self.folder, TestRequest())
        self.assertTrue(view.has_local())

    def test_folder_not_has_local(self):
        self._make_one()
        view = FolderView(self.folder, TestRequest())
        self.assertFalse(view.has_local())


ftest_suite = ZopeTestCase.FunctionalDocFileSuite('folder.txt',
                        setUp=setupVocabulary,
                        tearDown=clearVocabulary,
                        )

ftest_suite.layer = FunctionalLayer

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BatchViewTests))
    suite.addTest(unittest.makeSuite(FolderContentsViewTests))
    suite.addTest(unittest.makeSuite(FolderViewTests))
    suite.addTest(unittest.TestSuite((ftest_suite,)))
    return suite
