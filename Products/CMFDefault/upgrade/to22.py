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

from Products.CMFCore.interfaces import IWorkflowDefinition
from Products.CMFCore.utils import getToolByName

_KNOWN_IMPORT_STEPS = (
    'actions',
    'caching_policy_mgr',
    'catalog',
    'componentregistry',
    'content_type_registry',
    'cookie_authentication',
    'mailhost',
    'properties',
    'rolemap',
    'skins',
    'toolset',
    'typeinfo',
    'various',
    'workflow',
    )

_KNOWN_EXPORT_STEPS = (
    'actions',
    'caching_policy_mgr',
    'catalog',
    'componentregistry',
    'content_type_registry',
    'cookieauth',
    'mailhost',
    'properties',
    'rolemap',
    'skins',
    'step_registries',
    'toolset',
    'typeinfo',
    'workflows',
    )

def check_setup_tool(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    registry = tool.getImportStepRegistry()
    steps = registry.listSteps()
    for step in _KNOWN_IMPORT_STEPS:
        if step in steps:
            return True
    registry = tool.getExportStepRegistry()
    steps = registry.listSteps()
    for step in _KNOWN_EXPORT_STEPS:
        if step in steps:
            return True
    return False

def upgrade_setup_tool(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    registry = tool.getImportStepRegistry()
    steps = registry.listSteps()
    for step in _KNOWN_IMPORT_STEPS:
        if step in steps:
            registry.unregisterStep(step)
            tool._p_changed = True
            logger.info("Import step '%s' locally unregistered." % step)
    registry = tool.getExportStepRegistry()
    steps = registry.listSteps()
    for step in _KNOWN_EXPORT_STEPS:
        if step in steps:
            registry.unregisterStep(step)
            tool._p_changed = True
            logger.info("Export step '%s' locally unregistered." % step)

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
        content_icon = getattr(ti, 'content_icon', None)
        if content_icon is not None:
            return True
        if not ti.getProperty('add_view_expr') and \
                ti.getProperty('content_meta_type') != 'Discussion Item':
            return True
    return False

def upgrade_type_properties(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        changed = False
        content_icon = getattr(ti, 'content_icon', None)
        if content_icon is not None:
            del ti.content_icon
            if content_icon and not ti.getProperty('icon_expr'):
                icon_expr = 'string:${portal_url}/%s' % content_icon
                ti._updateProperty('icon_expr', icon_expr)
            changed = True
        if not ti.getProperty('add_view_expr') and \
                ti.getProperty('content_meta_type') != 'Discussion Item':
            ti._updateProperty('add_view_expr',
                               'string:${folder_url}/++add++%s'
                               % quote(ti.getId()))
            changed = True
        if changed:
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
                 'login': 'login_icon.png',
                 'join': 'join_icon.png',
                 'preferences': 'preferences_icon.png',
                 'logout': 'logout_icon.png',
                 'addFavorite': 'addfavorite_icon.png',
                 'mystuff': 'user_icon.png',
                 'favorites': 'favorite_icon.png',
                 'reply': 'reply_icon.png',
                 'syndication': 'syndication_icon.png',
                 'interfaces': 'interfaces_icon.png',
                 'folderContents': 'folder_icon.png',
                 'manage_members': 'members_icon.png',
                 'undo': 'undo_icon.png',
                 'configPortal': 'tool_icon.png',
                 }

def check_type_actions(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    ttool = getToolByName(tool, 'portal_types')
    for ti in ttool.listTypeInfo():
        for ai in ti.listActions():
            if not ai.getIconExpression() and ai.getId() in _ACTION_ICONS:
                return True
    return False

def upgrade_type_actions(tool):
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

def check_workflow_definitions(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    wtool = getToolByName(tool, 'portal_workflow')
    for obj in wtool.objectValues():
        if IWorkflowDefinition.providedBy(obj):
            for t in obj.transitions.values():
                if not t.actbox_icon and t.getId() in _ACTION_ICONS:
                    return True
            for w in obj.worklists.values():
                if not w.actbox_icon and w.getId() in _ACTION_ICONS:
                    return True
    return False

def upgrade_workflow_definitions(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    wtool = getToolByName(tool, 'portal_workflow')
    for wf in wtool.objectValues():
        changed = False
        if IWorkflowDefinition.providedBy(wf):
            for t in wf.transitions.values():
                if not t.actbox_icon and t.getId() in _ACTION_ICONS:
                    icon = _ACTION_ICONS[t.getId()]
                    t.actbox_icon = '%(portal_url)s/' + icon
                    changed = True
            for w in wf.worklists.values():
                if not w.actbox_icon and w.getId() in _ACTION_ICONS:
                    icon = _ACTION_ICONS[w.getId()]
                    w.actbox_icon = '%(portal_url)s/' + icon
                    changed = True
        if changed:
            logger.info("WorkflowDefinition '%s' changed." % wf.getId())

def check_action_properties(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    atool = getToolByName(tool, 'portal_actions')
    for category in atool.objectValues():
        for action in category.listActions():
            if not action.icon_expr and action.getId() in _ACTION_ICONS:
                return True
    return False

def upgrade_action_properties(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    atool = getToolByName(tool, 'portal_actions')
    for category in atool.objectValues():
        for action in category.listActions():
            if not action.icon_expr and action.getId() in _ACTION_ICONS:
                icon = _ACTION_ICONS[action.getId()]
                icon = 'string:${portal_url}/%s' % icon
                action._setPropValue('icon_expr', icon)
                logger.info("Action '%s' changed." % action.getId())

def check_catalog_columns(tool):
    """2.1.x to 2.2.0 upgrade step checker
    """
    ctool = getToolByName(tool, 'portal_catalog')
    columns = ctool.schema()
    if 'getIcon' in columns:
        return True
    if 'getIconURL' not in columns:
        return True
    return False

def upgrade_catalog_columns(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    ctool = getToolByName(tool, 'portal_catalog')
    columns = ctool.schema()
    if 'getIcon' in columns:
        ctool.delColumn('getIcon')
        logger.info("Catalog column 'getIcon' deleted.")
    if 'getIconURL' not in columns:
        ctool.addColumn('getIconURL')
        logger.info("Catalog column 'getIconURL' added.")
