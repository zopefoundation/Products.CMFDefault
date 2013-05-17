##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Upgrade steps to CMFDefault views_support 2.3.
"""

import logging

from Products.CMFCore.utils import getToolByName


_ACTION_URLS = {
    'user/login': 'string:${portal_url}/@@login.html',
    'user/join': 'string:${portal_url}/@@join.html',
    'user/change_password': 'string:${portal_url}/@@password.html',
    'user/preferences': 'string:${portal_url}/@@preferences.html',
    'user/logout': 'string:${portal_url}/@@logout.html',
    'user/logged_in': 'string:${portal_url}/@@logged_in.html',
    'object/syndication': 'string:${folder_url}/@@syndicate.html',
    'global/manage_members': 'string:${portal_url}/@@members.html',
    'global/members_register': 'string:${portal_url}/@@join.html',
    'global/search_form': 'string:${portal_url}/@@search_form.html',
    'global/search': 'string:${portal_url}/@@search.html',
    'global/configPortal': 'string:${portal_url}/@@configure.html'}

def check_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    atool = getToolByName(tool, 'portal_actions')
    for k, v in _ACTION_URLS.iteritems():
        category_id, action_id = k.split('/')
        try:
            obj = atool[category_id][action_id]
        except KeyError:
            continue
        prop = obj.getProperty('url_expr')
        if prop != v:
                return True
    return False

def upgrade_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    atool = getToolByName(tool, 'portal_actions')
    for k, v in _ACTION_URLS.iteritems():
        category_id, action_id = k.split('/')
        try:
            obj = atool[category_id][action_id]
        except KeyError:
            continue
        prop = obj.getProperty('url_expr')
        if prop != v:
            obj._setPropValue('url_expr', v)
            logger.info("Updated '{0}' action.".format(k))

_ALIASES = {
    'CMF BTree Folder': {'sharing': '@@sharing.html'},
    'Discussion Item': {'(Default)': '@@view.html', 'view': '@@view.html'},
    'Document': {'gethtml': '@@source.html'},
    'File': {'view': '@@view.html'},
    'Folder': {'sharing': '@@sharing.html'},
    'Image': {'view': '@@view.html'},
    'News Item': {'gethtml': '@@source.html'}}

def check_type_aliases(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    ttool = getToolByName(tool, 'portal_types')
    for ti_id, new_aliases in _ALIASES.iteritems():
        ti = ttool[ti_id]
        for k, v in new_aliases.iteritems():
            if ti.queryMethodID(k) != v:
                return True
    return False

def upgrade_type_aliases(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    ttool = getToolByName(tool, 'portal_types')
    logger = logging.getLogger('GenericSetup.upgrade')
    for ti_id, new_aliases in _ALIASES.iteritems():
        changed = False
        ti = ttool[ti_id]
        for k, v in new_aliases.iteritems():
            if ti.queryMethodID(k) != v:
                aliases = ti.getMethodAliases()
                aliases[k] = v
                ti.setMethodAliases(aliases)
                changed = True
        if changed:
            logger.info("Updated '{0}' type.".format(ti_id))
