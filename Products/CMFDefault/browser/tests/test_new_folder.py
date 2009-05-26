##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test Products.CMFDefault.browser.new_folder BrowserView tests
$Id$
"""

import unittest

from AccessControl.SecurityManagement import newSecurityManager

from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.tests.base.dummy import DummyUserFolder, DummyContent
from Products.CMFCore.interfaces import IPropertiesTool

from Products.CMFDefault.browser.new_folder import ContentsView

class FolderBrowserViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        # maybe there is a base class for this?
        self.site = site = DummySite('site')
        self.sm = getSiteManager()
        mtool = site._setObject('portal_membership', DummyTool())
        ptool = site._setObject('portal_properties', DummyTool())
        self.sm.registerUtility(ptool, IPropertiesTool)
        ttool = site._setObject('portal_types', DummyTool())
        utool = site._setObject('portal_url', DummyTool())
        folder = PortalFolder('test_folder')
        self.folder = site._setObject('test_folder', folder)
    
    def test_view(self):
        view = ContentsView(self.folder, TestRequest())
        self.failUnless(IBrowserPublisher.providedBy(view))
        
    def test_up_info(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals({'url':u'', 'id':u'Root', 'icon':u''}, view.up_info())
        
    def test_layout_fields(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals(view.layout_fields(), [])
    
    def test_is_orderable(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.is_orderable())
        
    def test_sort_can_be_changed(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.can_sort_be_changed())
    
    def test_has_subobjects(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.has_subobjects())
        
    def test_check_clipboard_data(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.check_clipboard_data())
    
    def test_check_validator(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals(view.validate_items(), [u'Please select one or more items first.'])
        self.assertEquals(view.validate_items(data={'foo':True}), [])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderBrowserViewTests))
    return suite
    
# bin/test -s ~/CMF-Sandbox/cmf-trunk/src/Products.CMFDefault/Products/CMFDefault/browser