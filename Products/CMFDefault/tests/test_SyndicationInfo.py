"""
Unit tests for the SyndicationInfo adapter
"""

import unittest

from zope.interface.verify import verifyClass

from Products.CMFCore.tests.base.testcase import TransactionalTest


class SyndicationInfoTests(TransactionalTest):
    
    def _getTargetClass(self):
        from Products.CMFDefault.SyndicationInfo import SyndicationInfo
        return SyndicationInfo
    
    def test_inteface(self):
        from Products.CMFCore.interfaces import ISyndicationInfo
        verifyClass(ISyndicationInfo, self._getTargetClass())
    
    def test_get_info(self):
        pass
    
    def test_set_info(self):
        pass
    
    def revert(self):
        pass
    
    def test_site_settings(self):
        pass
    
    def test_enabled(self):
        pass
    
    def test_enable(self):
        pass
    
    def test_disable(self):
        pass
    

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SyndicationInfoTests),
        ))
