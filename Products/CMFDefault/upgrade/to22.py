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
"""Upgrade steps to CMFDefault 2.2.

$Id$
"""
import logging
from urllib import quote

from Acquisition import aq_inner
from Acquisition import aq_parent
from zope.component.interfaces import ComponentLookupError

from Products.CMFCore.utils import getToolByName

def check_root_site_manager(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    portal = aq_parent(aq_inner(tool))
    try:
        components = portal.getSiteManager()
    except ComponentLookupError:
        return True
    return components.__name__ != '++etc++site'

def upgrade_root_site_manager(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    try:
        components = portal.getSiteManager()
    except ComponentLookupError:
        logger.warning("Site manager missing.")
        return
    components.__name__ = '++etc++site'
    logger.info("Site manager name changed to '++etc++site'.")

def check_root_properties(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    portal = aq_parent(aq_inner(tool))
    return not portal.hasProperty('enable_actionicons')

def upgrade_root_properties(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    portal.manage_addProperty('enable_actionicons', False, 'boolean')
    logger.info("'enable_actionicons' property added.")

def check_type_properties(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        if ti.getProperty('add_view_expr'):
            continue
        if ti.getProperty('content_meta_type') == 'Discussion Item':
            continue
        return True
    return False

def upgrade_type_properties(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        if ti.getProperty('add_view_expr'):
            continue
        if ti.getProperty('content_meta_type') == 'Discussion Item':
            continue
        ti._updateProperty('add_view_expr',
                           'string:${folder_url}/++add++%s'
                           % quote(ti.getId()))
        logger.info("TypeInfo '%s' changed." % ti.getId())

_ACTION_ICONS = {'download': 'download_icon.png',
                 'edit': 'edit_icon.png',
                 'folderContents': 'folder_icon.png',
                 'localroles': 'localroles_icon.png',
                 'metadata': 'metadata_icon.png',
                 'view': 'preview_icon.png',
                 'publish': 'approve_icon.png',
                 'reject': 'reject_icon.png',
                 'retract': 'retract_icon.png',
                 'submit': 'submit_icon.png',
                 'reviewer_queue': 'worklist_icon.png',
                 }

def check_action_icons(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        for ai in ti.listActions():
            if not ai.getIconExpression() and ai.getId() in _ACTION_ICONS:
                return True
    return False

def add_action_icons(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        changed = False
        for ai in ti.listActions():
            if not ai.getIconExpression() and ai.getId() in _ACTION_ICONS:
                ai.setIconExpression('string:${portal_url}/%s'
                                     % _ACTION_ICONS[ai.getId()])
                changed = True
        if changed:
            logger.info("TypeInfo '%s' changed." % ti.getId())
