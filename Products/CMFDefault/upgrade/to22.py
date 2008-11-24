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

def upgrade_default(tool):
    """2.1.x to 2.2.0 upgrade step handler
    """
    portal = aq_parent(aq_inner(tool))
    logger = logging.getLogger('GenericSetup.upgrade')
    upgrade_CMFSite_object(portal, logger)
    upgrade_TypeInfos(portal, logger)

def upgrade_CMFSite_object(portal, logger):
    components = portal.getSiteManager()
    if components.__name__ != '++etc++site':
        components.__name__ = '++etc++site'
        logger.info('Site manager name changed.')

    if not portal.hasProperty('enable_actionicons'):
        portal.manage_addProperty('enable_actionicons', False, 'boolean')
        logger.info("'enable_actionicons' property added.")

def upgrade_TypeInfos(portal, logger):
    ttool = portal.portal_types
    for ti in ttool.listTypeInfo():
        if ti.getProperty('content_meta_type') == 'Discussion Item':
            continue
        if ti.getProperty('add_view_expr'):
            continue
        ti._updateProperty('add_view_expr',
                           'string:${folder_url}/++add++%s'
                           % quote(ti.getId()))
        logger.info("TypeInfo '%s' changed." % ti.getId())

