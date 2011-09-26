##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for SyndicationTool module.
"""

import unittest
import Testing

from DateTime.DateTime import DateTime
from zope.component import getSiteManager
from zope.component import queryAdapter
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.tests.base.testcase import SecurityTest


class Dummy:

    def getId(self):
        return 'dummy'


class DummyInfo:

    def __init__(self, context):
        self.context = context

    def __call__(self):
        pass

    @property
    def enabled(self):
        if hasattr(self.context, 'enabled'):
            return self.context.enabled
        return False

    def enable(self):
        self.context.enabled = True

    def disable(self):
        self.context.enabled = False

    def set_info(self, **kw):
        for k, v in kw.items():
            setattr(self.context, k, v)

    def get_info(self):
        if hasattr(self.context, 'frequency'):
            # values set on context
            return {'frequency': self.context.frequency,
                    'period': self.context.period,
                    'base': self.context.base,
                    'max_items': self.context.max_items}
        #values from syndication tool
        return {'frequency': '1', 'period': 'daily',
                'base': DateTime('2010/10/04 12:00:00 GMT'), 'max_items': 15}

class SyndicationToolTests(SecurityTest):

    def _getTargetClass(self):
        from Products.CMFDefault.SyndicationTool import SyndicationTool
        return SyndicationTool

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeContext(self):
        from Products.CMFCore.interfaces import IFolderish, ISyndicationInfo
        self.folder = folder = Dummy()
        alsoProvides(folder, IFolderish)
        sm = getSiteManager()
        sm.registerAdapter(DummyInfo, [IFolderish], ISyndicationInfo)
        return folder

    def tearDown(self):
        cleanUp()
        SecurityTest.tearDown(self)

    def test_interfaces(self):
        from Products.CMFCore.interfaces import ISyndicationTool

        verifyClass(ISyndicationTool, self._getTargetClass())

    def test_empty(self):
        ONE_MINUTE = (24.0 * 60.0) / 86400

        tool = self._makeOne()

        self.assertEqual(tool.syUpdatePeriod, 'daily')
        self.assertEqual(tool.syUpdateFrequency, 1)
        self.failUnless(DateTime() - tool.syUpdateBase < ONE_MINUTE)
        self.failIf(tool.isAllowed)
        self.assertEqual(tool.max_items, 15)

    def test_editProperties_normal(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.editProperties(updatePeriod=PERIOD,
                            updateFrequency=FREQUENCY,
                            updateBase=NOW,
                            isAllowed=True,
                            max_items=MAX_ITEMS,
                           )

        self.assertEqual(tool.syUpdatePeriod, PERIOD)
        self.assertEqual(tool.syUpdateFrequency, FREQUENCY)
        self.assertEqual(tool.syUpdateBase, NOW)
        self.failUnless(tool.isAllowed)
        self.assertEqual(tool.max_items, MAX_ITEMS)

    def test_editProperties_coercing(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.editProperties(updatePeriod=PERIOD,
                            updateFrequency='%d' % FREQUENCY,
                            updateBase=NOW.ISO(),
                            isAllowed='True',
                            max_items='%d' % MAX_ITEMS,
                           )

        self.assertEqual(tool.syUpdatePeriod, PERIOD)
        self.assertEqual(tool.syUpdateFrequency, FREQUENCY)
        self.assertEqual(tool.syUpdateBase, DateTime(NOW.ISO()))
        self.failUnless(tool.isAllowed)
        self.assertEqual(tool.max_items, MAX_ITEMS)

    def test_object_not_syndicatable(self):
        tool = self._makeOne()
        self.assertFalse(tool.isSyndicationAllowed(Dummy))

    def test_object_is_syndicatable(self):
        from Products.CMFCore.interfaces import ISyndicationInfo
        self._makeOne()
        context = self._makeContext()
        adapter = queryAdapter(context, ISyndicationInfo)
        self.assertTrue(adapter is not None)

    def test_object_syndication_is_disabled(self):
        tool = self._makeOne()
        context = self._makeContext()
        self.assertFalse(tool.isSyndicationAllowed(context))

    def test_enable_object_syndication(self):
        tool = self._makeOne()
        tool.isAllowed = True
        context = self._makeContext()
        tool.enableSyndication(context)
        self.assertTrue(tool.isSyndicationAllowed(context))

    def test_editSyInformationProperties_normal(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.isAllowed = True
        context = self._makeContext()
        tool.enableSyndication(context)

        tool.editSyInformationProperties(context,
                                         updatePeriod=PERIOD,
                                         updateFrequency=FREQUENCY,
                                         updateBase=NOW,
                                         max_items=MAX_ITEMS,
                                        )
        self.assertEqual(tool.getSyndicationInfo(context),
                             {'frequency': FREQUENCY, 'period': PERIOD,
                              'base': NOW, 'max_items': MAX_ITEMS})

    def test_editSyInformationProperties_coercing(self):
        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        tool = self._makeOne()
        tool.isAllowed = True
        context = self._makeContext()
        tool.enableSyndication(context)

        tool.editSyInformationProperties(context,
                                         updatePeriod=PERIOD,
                                         updateFrequency='%d' % FREQUENCY,
                                         updateBase=NOW.ISO(),
                                         max_items='%d' % MAX_ITEMS,
                                        )
        self.assertEqual(tool.getSyndicationInfo(context),
                             {'frequency': FREQUENCY, 'period': PERIOD,
                              'base': DateTime(NOW.ISO()),
                              'max_items': MAX_ITEMS})

    def test_editProperties_isAllowedOnly(self):
        # Zope 2.8 crashes if we don't edit all properties.
        # This is because Zope now raises AttributeError
        # instead of KeyError in editProperties().
        tool = self._makeOne()
        tool.editProperties(isAllowed=1)

        self.failUnless(tool.isAllowed)

    def test_getSyndicatableContent(self):
        # http://www.zope.org/Collectors/CMF/369
        # Make sure we use a suitable base class call when determining
        # syndicatable content
        from Products.CMFCore.PortalFolder import PortalFolder
        from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
        from Products.CMFCore.TypesTool import TypesTool

        PERIOD = 'hourly'
        FREQUENCY = 4
        NOW = DateTime()
        MAX_ITEMS = 42

        getSiteManager().registerUtility(TypesTool(), ITypesTool)
        self.app._setObject('pf', PortalFolder('pf'))
        self.app._setObject('bf', CMFBTreeFolder('bf'))
        tool = self._makeOne()
        tool.editProperties(updatePeriod=PERIOD,
                            updateFrequency=FREQUENCY,
                            updateBase=NOW,
                            isAllowed=True,
                            max_items=MAX_ITEMS,
                           )

        self.assertEqual(len(tool.getSyndicatableContent(self.app.pf)), 0)
        self.assertEqual(len(tool.getSyndicatableContent(self.app.bf)), 0)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SyndicationToolTests),
        ))
