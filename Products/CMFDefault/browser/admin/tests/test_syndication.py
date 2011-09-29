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
"""Tests for portal syndication form.
"""

import unittest

from zope.component import getSiteManager
from zope.interface import implements
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.interface import alsoProvides
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFDefault.browser.test_utils import DummyRequest


class DummySyndicationTool(object):

    isAllowed = False
    syUpdatePeriod = updatePeriod = "daily"
    syUpdateFrequency = updateFrequency = 1
    syUpdateBase = updateBase = ""
    max_items = 15

    def getProperty(self, key, default):
        return getattr(self, key, default)

    def editProperties(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def isSiteSyndicationAllowed(self):
        return self.isAllowed

    def hasProperty(self, key):
        return getattr(self, key)

    def _updateProperty(self, key, value):
        setattr(self, key, value)


class DummySyndicationAdapter(object):

    def __init__(self, context):
        self.context = context


class DummyPropertiesTool(DummyTool):

    def getProperty(self, key, default):
        return getattr(self, key, default)


class SyndicationViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        self.site = DummySite('site')
        alsoProvides(self.site, IPropertiesTool)
        sm = getSiteManager()
        sm.registerUtility(DummySyndicationTool(), ISyndicationTool)
        sm.registerUtility(DummyTool(), IActionsTool)
        sm.registerUtility(DummyTool(), IMembershipTool)
        sm.registerUtility(DummyTool().__of__(self.site), IURLTool)
        sm.registerUtility(DummyPropertiesTool(), IPropertiesTool)
        from Products.CMFDefault.browser.admin.syndication import ISyndicationSchema
        sm.registerAdapter(self._getTargetAdapter(), (IFolderish, ), ISyndicationSchema)

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from Products.CMFDefault.browser.admin.syndication import Site
        request = DummyRequest(ACTUAL_URL="http://example.com")
        alsoProvides(request, IUserPreferredCharsets)
        return Site(self.site, request)

    def _getTargetAdapter(self):
        from Products.CMFDefault.browser.admin.syndication import SyndicationToolSchemaAdapter
        return SyndicationToolSchemaAdapter

    def test_enabled(self):
        view = self._getTargetClass()
        self.assertFalse(view.enabled)

    def test_disabled(self):
        view = self._getTargetClass()
        self.assertTrue(view.disabled)

    def test_handle_enable(self):
        view = self._getTargetClass()
        view.handle_enable("enable", {})
        self.assertTrue(view.enabled)
        self.assertEqual(view.status, u"Syndication enabled.")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20enabled.")

    def test_handle_change(self):
        import datetime
        today = datetime.datetime.now()
        view = self._getTargetClass()
        view.adapters = {DummySyndicationAdapter: ISyndicationInfo}
        self.assertEqual(view.getContent().period, 'daily')
        self.assertEqual(view.getContent().frequency, 1)
        self.assertEqual(view.getContent().base, "")
        self.assertEqual(view.getContent().max_items, 15)
        data = {'frequency':3, 'period':'weekly', 'base':today,
                'max_items':10}
        view.handle_change("change", data)
        self.assertEqual(view.getContent().period, 'weekly')
        self.assertEqual(view.getContent().frequency, 3)
        self.assertEqual(view.getContent().base, today)
        self.assertEqual(view.getContent().max_items, 10)
        self.assertEqual(view.status, u"Syndication settings changed.")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20settings%20changed.")

    def test_handle_disable(self):
        view = self._getTargetClass()
        view.syndtool.isAllowed = True
        self.assertTrue(view.enabled)
        view.handle_disable("disable", {})
        self.assertTrue(view.disabled)
        self.assertEqual(view.status, u"Syndication disabled.")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20disabled.")


class FolderSyndicationTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        from Products.CMFDefault.SyndicationInfo import SyndicationInfo

        self.site = DummySite('site')
        self.syndtool = DummySyndicationTool()
        sm = getSiteManager()
        sm.registerUtility(self.syndtool, ISyndicationTool)
        sm.registerAdapter(SyndicationInfo, [IFolderish], ISyndicationInfo)
        sm.registerUtility(DummyTool(), IActionsTool)
        sm.registerUtility(DummyTool(), IMembershipTool)
        sm.registerUtility(DummyTool().__of__(self.site), IURLTool)

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from Products.CMFDefault.browser.admin.syndication import Syndicate
        self.site._setObject('folder', DummyFolder('Folder'))
        alsoProvides(self.site, IFolderish)
        request = DummyRequest(ACTUAL_URL="http://example.com")
        alsoProvides(request, IUserPreferredCharsets)
        return Syndicate(self.site, request)

    def test_allowed(self):
        view = self._getTargetClass()
        self.assertFalse(view.allowed)

    def test_adapter(self):
        view = self._getTargetClass()
        self.assertTrue(ISyndicationInfo.providedBy(view.adapter))

    def test_enabled(self):
        view = self._getTargetClass()
        self.assertFalse(view.enabled())

    def test_disabled(self):
        view = self._getTargetClass()
        self.assertTrue(view.disabled())

    def test_handle_enable(self):
        self.syndtool.isAllowed = 1
        view = self._getTargetClass()
        view.handle_enable("enable", {})
        self.assertTrue(view.enabled())
        self.assertEqual(view.status, u"Syndication enabled.")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20enabled.")

    def test_handle_disable(self):
        self.syndtool.isAllowed = 1
        view = self._getTargetClass()
        view.adapter.enable()
        view.handle_disable("disable", {})
        self.assertFalse(view.enabled())
        self.assertEqual(view.status, u"Syndication disabled.")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20disabled.")

    #def test_handle_change(self):
        #view = self._getTargetClass()
        #values = {'frequency': 4, 'period': 'weekly', 'base': '2010-01-01',
                  #'max_items': 25}
        #view.handle_change("change", values)
        #self.assertEqual(view.adapter.get_info(), values)
        #self.assertEqual(view.status, u"Syndication settings changed.")
        #self.assertEqual(view.request.RESPONSE.location,
            #"http://www.foobar.com/bar/site?portal_status_message="
            #"Syndication%20settings%20changed.")

    #def test_handle_revert(self):
        #view = self._getTargetClass()
        #values = {'frequency': 4, 'period': 'weekly', 'base': '2010-01-01',
                  #'max_items': 25}
        #view.handle_change("change", values)
        #view.handle_revert("", values)
        #self.assertNotEqual(view.adapter.get_info(), values)
        #self.assertEqual(view.status, u"Syndication reset to site default.")
        #self.assertEqual(view.request.RESPONSE.location,
            #"http://www.foobar.com/bar/site?portal_status_message="
            #"Syndication%20reset%20to%20site%20default.")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SyndicationViewTests))
    suite.addTest(unittest.makeSuite(FolderSyndicationTests))
    return suite
