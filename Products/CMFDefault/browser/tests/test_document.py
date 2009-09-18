##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Test Products.CMFDefault.browser.document

$Id$
"""

import unittest
from Testing import ZopeTestCase
from Products.Five.schema import Zope2VocabularyRegistry

from Products.CMFDefault.testing import FunctionalLayer

def _setupVocabulary(ztc):
    from zope.schema.vocabulary import setVocabularyRegistry
    setVocabularyRegistry(Zope2VocabularyRegistry())

def _clearVocabulary(ztc):
    from zope.schema.vocabulary import _clear
    _clear()


ftest_suite = ZopeTestCase.FunctionalDocFileSuite(
                'document.txt',
                setUp=_setupVocabulary,
                tearDown=_clearVocabulary,
               )
ftest_suite.layer = FunctionalLayer

def test_suite():
    return unittest.TestSuite((
        ftest_suite,
    ))
