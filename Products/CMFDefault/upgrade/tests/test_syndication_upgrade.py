##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Syndication Upgrade tests.
"""

import datetime
import unittest
from Testing import ZopeTestCase

import transaction

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser
from Products.CMFDefault.testing import FunctionalLayer
from zope.site.hooks import setSite


class FunctionalUpgradeTestCase(ZopeTestCase.FunctionalTestCase):

    layer = FunctionalLayer
    _setup_fixture = 0

    def setUp(self):
        super(FunctionalUpgradeTestCase, self).setUp()

    def makeOne(self):
        """Create an old style SyndicatonInformation for a folder"""
        from Products.CMFCore.PortalFolder import PortalFolder
        from Products.CMFDefault.SyndicationInfo import SyndicationInformation
        folder = PortalFolder(syndicated_folder)
        info = SyndicationInformation()
        info.syndBase = datetime.datetime.now()
        info.syndPeriod = 1
        info.syndFrequency = 1
        info.max_items = 5

    def test_nothing(self):
        pass


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FunctionalUpgradeTestCase),
        ))