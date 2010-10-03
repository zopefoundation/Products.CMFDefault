"""
Unit tests for the SyndicationInfo adapter
"""

import unittest

from DateTime.DateTime import DateTime

from zope.interface.verify import verifyClass

from Products.CMFCore.tests.base.testcase import TransactionalTest


class SyndicationInfoTests(TransactionalTest):
    
    def setUp(self):
        super(SyndicationInfoTests, self).setUp()
        from Products.CMFCore.PortalFolder import PortalFolder
        self.root._setObject('portal', PortalFolder('portal'))
        self.portal = self.root.portal
        tool = self.portal._setObject('portal_syndication',
                                DummySyndicationTool())
        self.syndication_tool = self.portal.portal_syndication
    
    def _getTargetClass(self):
        from Products.CMFDefault.SyndicationInfo import SyndicationInfo
        return SyndicationInfo
    
    def _makeOne(self):
        from Products.CMFCore.PortalFolder import PortalFolder
        self.portal._setObject('folder', PortalFolder('folder'))
        return self._getTargetClass()(self.portal.folder)
    
    def test_inteface(self):
        from Products.CMFCore.interfaces import ISyndicationInfo
        verifyClass(ISyndicationInfo, self._getTargetClass())
    
    def test_site_settings(self):
        adapter = self._makeOne()
        self.assertTrue(adapter.site_settings is self.syndication_tool)
    
    def test_get_info(self):
        adapter = self._makeOne()
        self.assertEqual(adapter.get_info(),
                        {'max_items': 15, 'frequency': 1, 'period': 'daily',
                        'base': DateTime('2010/10/03 12:00:00 GMT+0')})
    
    def test_set_info(self):
        adapter = self._makeOne()
        settings = {'max_items': 10, 'frequency': 7, 'period': 'daily',
        'base': DateTime()}
        self.assertNotEqual(adapter.get_info(), settings)
        adapter.set_info(**settings)
        self.assertEqual(adapter.get_info(), settings)
    
    def revert(self):
        adapter = self._makeOne()
        settings = {'max_items': 20, 'frequency': 1, 'period': 'monthly',
        'base': DateTime()}
        adapter.set_info(**settings)
        self.assertEqual(adapter.get_info(), settings)
        adapter.revert()
        self.assertNotEqual(adapter.get_info(), settings)
    
    def test_enabled(self):
        adapter = self._makeOne()
        self.assertFalse(adapter.enabled)
    
    def test_enable(self):
        adapter = self._makeOne()
        self.syndication_tool.isAllowed = 1
        adapter.enable()
        self.assertTrue(adapter.enabled)
    
    def test_disable(self):
        adapter = self._makeOne()
        self.syndication_tool.isAllowed = 1
        adapter.enable()
        self.assertTrue(adapter.enabled)
        adapter.disable()
        self.assertFalse(adapter.disable())


class DummySyndicationTool(object):
    
    isAllowed = 0
    syUpdatePeriod = 'daily'
    syUpdateFrequency = 1
    syUpdateBase = DateTime('2010/10/03 12:00:00 GMT+0')
    max_items = 15
    
    def manage_fixupOwnershipAfterAdd(self):
        pass

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SyndicationInfoTests),
        ))
