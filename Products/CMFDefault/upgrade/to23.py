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
"""Upgrade steps to CMFDefault 2.3.
"""

import logging

from AccessControl.User import UserFolder as OldUserFolder
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.userfolder import UserFolder
from Products.CMFCore.utils import getToolByName

_MARKER = object()

def check_cookie_crumbler(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    cctool = getToolByName(tool, 'cookie_authentication', None)
    if cctool is None:
        return False
    cctool = aq_base(cctool)
    for name in ('auto_login_page', 'unauth_page', 'logout_page'):
        if getattr(cctool, name, _MARKER) is not _MARKER:
            return True
    return False

def upgrade_cookie_crumbler(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    cctool = getToolByName(tool, 'cookie_authentication', None)
    if cctool is None:
        return
    cctool = aq_base(cctool)
    for name in ('auto_login_page', 'unauth_page', 'logout_page'):
        if getattr(cctool, name, _MARKER) is not _MARKER:
            delattr(cctool, name)
            logger.info("Cookie crumbler property '%s' removed." % name)

def check_setup_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    registry = tool.getToolsetRegistry()
    try:
        info = registry.getRequiredToolInfo('acl_users')
        if info['class'] == 'AccessControl.User.UserFolder':
            return True
    except KeyError:
        return False
    return False

def upgrade_setup_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    registry = tool.getToolsetRegistry()
    try:
        info = registry.getRequiredToolInfo('acl_users')
        if info['class'] == 'AccessControl.User.UserFolder':
            info['class'] = 'OFS.userfolder.UserFolder'
            tool._p_changed = True
            logger.info("Updated class registered for 'acl_users'.")
    except KeyError:
        return

def check_acl_users(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            return True
    return False

def upgrade_acl_users(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            users.__class__ = UserFolder
            users._ofs_migrated = True
            users._p_changed = True
            logger.info("Updated UserFolder class.")
