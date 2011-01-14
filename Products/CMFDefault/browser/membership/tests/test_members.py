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
""" Tests for membership views """

import unittest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser
from Testing import ZopeTestCase

from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummySite, DummyTool
from Products.CMFCore.tests.base.dummy import (
            DummyUserFolder, DummyUser
            )

from Products.CMFDefault.browser.membership.members import Manage, MemberProxy
from Products.CMFDefault.testing import FunctionalLayer


class DummyUser(DummyUser):

    def getProperty(self, attr):
        return None


class DummyMemberTool(object):

    def __init__(self):
        self.members = {}

    def listMembers(self):
        return self.members.values()

    def addMember(self, member):
        self.members[member.getId()] = member

    def deleteMembers(self, member_ids):
        for i in member_ids:
            del self.members[i]

    def isAnonymousUser(self):
        return True

class MembershipViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        self.site = site = DummySite('site')
        self.sm = getSiteManager()
        self.mtool = site._setObject('portal_membership', DummyMemberTool())
        site._setObject('portal_actions', DummyTool())
        site._setObject('portal_url', DummyTool())

    def _make_one(self, name="DummyUser"):
        user = DummyUser(name)
        self.mtool.addMember(user)
        return user

    def _make_batch(self):
        """Add enough objects to force pagination"""
        batch_size = Manage._BATCH_SIZE
        for i in range(batch_size + 2):
            user_id = "Dummy%s" % i
            self._make_one(user_id)

    def test_getNavigationURL(self):
        url = 'http://example.com/members.html'
        self._make_batch()
        view = Manage(self.site, TestRequest(ACTUAL_URL=url))
        self.assertTrue(view._getNavigationURL(25) == url + "?form.b_start=25")

    def test_view(self):
        view = Manage(self.site, TestRequest())
        self.assertTrue(IBrowserPublisher.providedBy(view))

    def test_list_batch_items(self):
        user = self._make_one("Bob")
        view = Manage(self.site, TestRequest())
        view.member_fields()
        members = view.listBatchItems
        self.assertTrue(isinstance(members[0], MemberProxy))
        self.assertEquals(members[0].name, "Bob")

    def test_get_ids(self):
        view = Manage(self.site, TestRequest())
        self.assertEquals(
                        view._get_ids({'foo':'bar'}),
                        [])
        self.assertEquals(
                        sorted(
                            view._get_ids({'DummyUser1.select':True,
                                       'DummyUser2.select':False,
                                       'DummyUser3.select':True})
                            ),
                        ['DummyUser1', 'DummyUser3']
                        )
        self.assertEquals(
                        view._get_ids({'stupid.name.select.select':True}),
                        ['stupid.name.select']
        )

    def test_handle_select_for_deletion(self):
        view = Manage(self.site, TestRequest())
        self.assertTrue(view.guillotine == None)
        # Catch exception raised when template tries to render
        self.assertRaises(AttributeError,
                view.handle_select_for_deletion, None, {"Alice.select":True} )
        self.assertTrue(view.guillotine == "Alice")

    def test_handle_delete(self):
        self._make_one("Bob")
        view = Manage(self.site, TestRequest())
        self.assertFalse(self.mtool.listMembers() == [])
        # Catch exception raised when trying to redirect
        self.assertRaises(TypeError,
                         view.handle_delete, None, {"Bob.select":True}
                         )
        self.assertTrue(self.mtool.listMembers() == [])


ftest_suite = ZopeTestCase.FunctionalDocFileSuite('members.txt',
                        )


ftest_suite.layer = FunctionalLayer

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MembershipViewTests))
    suite.addTest(unittest.TestSuite((ftest_suite,)))
    return suite