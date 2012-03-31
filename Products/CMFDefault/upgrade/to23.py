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

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.userfolder import UserFolder
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.dottedname.resolve import resolve

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import SetupEnviron
from Products.GenericSetup.interfaces import IBody

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
    from AccessControl.User import UserFolder as OldUserFolder

    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            return True
    return False

def upgrade_acl_users(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    from AccessControl.User import UserFolder as OldUserFolder

    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            users.__class__ = UserFolder
            users._ofs_migrated = True
            users._p_changed = True
            logger.info("Updated UserFolder class.")

def check_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    atool = getToolByName(tool, 'portal_actions')
    try:
        atool.user.change_password
    except AttributeError:
        return True
    try:
        atool['global'].members_register # 'global' is a reserved word in Python
    except (KeyError, AttributeError):
        return True
    try:
        atool['global'].syndication # 'global' is a reserved word in Python
    except (KeyError, AttributeError):
        return True
    return False

def upgrade_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    atool = getToolByName(tool, 'portal_actions')
    environ = SetupEnviron()
    environ._should_purge = False
    getMultiAdapter((atool, environ), IBody).body = _ACTIONS_PASSWORD_XML
    logger.info("'change_password' action added.")
    getMultiAdapter((atool, environ), IBody).body = _ACTIONS_REGISTER_XML
    logger.info("'members_register' action added.")
    getMultiAdapter((atool, environ), IBody).body = _ACTIONS_SYNDICATION_XML
    logger.info("'portal syndication settings' action added.")

_ACTIONS_PASSWORD_XML = """\
<?xml version="1.0"?>
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="user" meta_type="CMF Action Category">
  <object insert-after="join" name="change_password" meta_type="CMF Action"
     i18n:domain="cmf_default">
   <property name="title" i18n:translate="">Change password</property>
   <property name="description"
      i18n:translate="">Change your password</property>
   <property name="url_expr">string:${portal_url}/password_form</property>
   <property name="link_target"></property>
   <property
      name="icon_expr">string:${portal_url}/preferences_icon.png</property>
   <property name="available_expr">member</property>
   <property name="permissions">
    <element value="Set own password"/>
   </property>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""

_ACTIONS_REGISTER_XML = """\
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="global" meta_type="CMF Action Category">
  <object name="members_register" meta_type="CMF Action"
     insert-after="manage_members" i18n:domain="cmf_default">
   <property name="title" i18n:translate="">Register a new member</property>
   <property name="description"
      i18n:translate="">Register a new portal member</property>
   <property name="url_expr">string:${portal_url}/join_form</property>
   <property name="link_target"></property>
   <property name="icon_expr">string:${portal_url}/join_icon.png</property>
   <property name="available_expr"></property>
   <property name="permissions">
    <element value="Manage users"/>
   </property>
   <property name="visible">False</property>
  </object>
 </object>
</object>
"""

_ACTIONS_SYNDICATION_XML = """\
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="global" meta_type="CMF Action Category">
  <object name="syndication" meta_type="CMF Action" i18n:domain="cmf_default">
   <property name="title" i18n:translate="">Site Syndication</property>
   <property name="description"
      i18n:translate="">Enable or disable syndication</property>
   <property
      name="url_expr">string:${portal_url}/@@syndication.html</property>
   <property name="link_target"></property>
   <property name="icon_expr">string:${portal_url}/tool_icon.png</property>
   <property name="available_expr"></property>
   <property name="permissions">
    <element value="Manage portal"/>
   </property>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""

def check_member_data_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    mdtool = getToolByName(tool, 'portal_memberdata')
    listed = mdtool.getProperty('listed')
    if listed == '':
        return True
    login_time = mdtool.getProperty('login_time')
    if login_time == '2000/01/01':
        return True
    last_login_time = mdtool.getProperty('last_login_time')
    if last_login_time == '2000/01/01':
        return True
    if not mdtool.hasProperty('fullname'):
        return True
    for prop_map in mdtool._propertyMap():
        if prop_map['id'] in ('email', 'fullname', 'last_login_time',
                              'listed', 'login_time', 'portal_skin'):
            if 'd' in prop_map.get('mode', 'wd'):
                return True
    return False

def upgrade_member_data_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    mdtool = getToolByName(tool, 'portal_memberdata')
    listed = mdtool.getProperty('listed')
    if listed == '':
        mdtool._updateProperty('listed', '')
        logger.info("Member data tool property 'listed' fixed.")
    login_time = mdtool.getProperty('login_time')
    if login_time == '2000/01/01':
        mdtool._updateProperty('login_time', '2000/01/01')
        logger.info("Member data tool property 'login_time' fixed.")
    last_login_time = mdtool.getProperty('last_login_time')
    if last_login_time == '2000/01/01':
        mdtool._updateProperty('last_login_time', '2000/01/01')
        logger.info("Member data tool property 'last_login_time' fixed.")
    if not mdtool.hasProperty('fullname'):
        prop_map = list(mdtool._properties)
        prop_map.insert(5, {'id': 'fullname', 'type': 'string', 'mode': 'w'})
        mdtool._properties = prop_map
        logger.info("Member data tool property 'fullname' added.")
    for prop_map in mdtool._propertyMap():
        changed = False
        if prop_map['id'] in ('email', 'fullname', 'last_login_time',
                              'listed', 'login_time', 'portal_skin'):
            if 'd' in prop_map.get('mode', 'wd'):
                prop_map['mode'] = 'w'
                changed = True
        if changed:
            mdtool._p_changed = True
            logger.info("Member data tool property modes fixed.")

_TOOL_UTILITIES = (
    ('caching_policy_manager', 'Products.CMFCore.interfaces.ICachingPolicyManager'),
    ('content_type_registry', 'Products.CMFCore.interfaces.IContentTypeRegistry'),
    ('cookie_authentication', 'Products.CMFCore.interfaces.ICookieCrumbler'),
    ('portal_actions', 'Products.CMFCore.interfaces.IActionsTool'),
    ('portal_calendar', 'Products.CMFCalendar.interfaces.ICalendarTool'),
    ('portal_catalog', 'Products.CMFCore.interfaces.ICatalogTool'),
    ('portal_memberdata', 'Products.CMFCore.interfaces.IMemberDataTool'),
    ('portal_membership', 'Products.CMFCore.interfaces.IMembershipTool'),
    ('portal_registration', 'Products.CMFCore.interfaces.IRegistrationTool'),
    ('portal_skins', 'Products.CMFCore.interfaces.ISkinsTool'),
    ('portal_types', 'Products.CMFCore.interfaces.ITypesTool'),
    ('portal_url', 'Products.CMFCore.interfaces.IURLTool'),
    ('portal_workflow', 'Products.CMFCore.interfaces.IWorkflowTool'),
)

def check_root_site_manager(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    portal = aq_parent(aq_inner(tool))
    try:
        sm = portal.getSiteManager()
    except ComponentLookupError:
        return True

    for tool_id, tool_interface in _TOOL_UTILITIES:
        tool_obj = getToolByName(portal, tool_id, default=None)
        try:
            iface = resolve(tool_interface)
        except ImportError:
            continue

        if tool_obj is not None and sm.queryUtility(iface) is None:
            return True

    return False

def upgrade_root_site_manager(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    try:
        sm = portal.getSiteManager()
    except ComponentLookupError:
        logger.warning("Site manager missing.")
        return

    for tool_id, tool_interface in _TOOL_UTILITIES:
        tool_obj = getToolByName(portal, tool_id, default=None)
        try:
            iface = resolve(tool_interface)
        except ImportError:
            continue

        if tool_obj is not None and sm.queryUtility(iface) is None:
            sm.registerUtility(tool_obj, iface)
            logger.info('Registered %s for interface %s' % (tool_id,
                                                            tool_interface))

def DateTime_to_datetime(Zope_DateTime):
    """
    Convert from Zope DateTime to Python datetime and strip timezone
    """
    from DateTime.DateTime import DateTime
    naive = DateTime(str(Zope_DateTime).rsplit(' ', 1)[0])
    return naive.asdatetime()

def change_to_adapter(SyndicationInformation, path=None):
    """
    Read values from the SyndicationInformation object and set them on
    the adapter and then delete the SyndicationInformation object
    """
    from zope.component import getAdapter
    from Products.CMFDefault.SyndicationInfo import ISyndicationInfo
    folder = aq_parent(aq_inner(SyndicationInformation))
    adapter = getAdapter(folder, ISyndicationInfo)
    adapter.period = SyndicationInformation.syUpdatePeriod
    adapter.base = DateTime_to_datetime(SyndicationInformation.syUpdateBase)
    adapter.frequency = SyndicationInformation.syUpdateFrequency
    adapter.max_items = SyndicationInformation.max_items
    if getattr(SyndicationInformation, 'isAllowed', False):
        adapter.enable()
    folder._delObject(SyndicationInformation.getId())

def check_syndication_tool(tool):
    """Convert if portal_syndication exists"""
    portal = aq_parent(aq_inner(tool))
    try:
        syndication = getToolByName(portal, "portal_syndication")
    except AttributeError:
        return False
    infos = portal.ZopeFind(portal,
                            obj_metatypes=["SyndicationInformation"],
                            search_sub=True)
    if infos != []:
        return True

def upgrade_syndication_tool(tool):
    """Replace SyndicatonInformation objects with SyndicationInfo adapters"""
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    syndication = getToolByName(portal, "portal_syndication")
    syndication.base = DateTime_to_datetime(syndication.syUpdateBase)
    syndication.enabled = syndication.isAllowed and True or False
    infos = portal.ZopeFindAndApply(portal,
                                    obj_metatypes=["SyndicationInformation"],
                                    search_sub=True,
                                    apply_func=change_to_adapter)
    logger.info("SyndicationTool updated and SyndicationInformation replaced by Annotations")

def check_root_properties(tool):
    """2.3.0-beta to 2.3.0 upgrade step checker
    """
    portal = aq_parent(aq_inner(tool))
    enable_actionicons = portal.getProperty('enable_actionicons')
    if isinstance(enable_actionicons, tuple):
        return True
    return False

def upgrade_root_properties(tool):
    """2.3.0-beta to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    enable_actionicons = portal.getProperty('enable_actionicons')
    if isinstance(enable_actionicons, tuple):
        enable_actionicons = bool(enable_actionicons[0])
        portal._updateProperty('enable_actionicons', enable_actionicons)
        logger.info("'enable_actionicons' property fixed.")
