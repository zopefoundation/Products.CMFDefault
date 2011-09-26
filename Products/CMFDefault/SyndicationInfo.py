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
""" SyndicationInfo is an adapter for IFolderish objects.
"""

from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ISyndicatable
from Products.CMFCore.interfaces import ISyndicationInfo
from Products.CMFCore.interfaces import ISyndicationTool


class SyndicationInformation(SimpleItem):
    #DEPRECATED
    """
    Existing implementation creates a full SimpleItem which is not directly
    editable
    """

    id='syndication_information'
    meta_type='SyndicationInformation'


class SyndicationInfo(object):
    """
    Annotations style adapter.
    Folders which can be syndicated are given the ISyndicatable interface
    Local syndication information is stored as a dictionary on the
    _syndication_info attribute of the folder
    """

    implements(ISyndicationInfo)
    adapts(IFolderish)
    key = "_syndication_info"

    def __init__(self, context):
        self.context = context

    @property
    def site_settings(self):
        """Get site syndication tool"""
        return getUtility(ISyndicationTool)

    def get_info(self):
        """
        Return syndication settings for the folder or from global site
        settings if there are none for the folder
        """
        info = getattr(self.context, self.key, None)
        if info is None:
            values = {'period': self.site_settings.syUpdatePeriod,
                     'frequency':self.site_settings.syUpdateFrequency,
                     'base': self.site_settings.syUpdateBase,
                     'max_items': self.site_settings.max_items}
            return values
        return info

    def set_info(self, period=None, frequency=None, base=None,
                max_items=None):
        """Folder has local values"""
        values = {'period': period, 'frequency': frequency,
                  'base': base, 'max_items': max_items}
        setattr(self.context, self.key, values)

    def revert(self):
        """Remove local values"""
        try:
            delattr(self.context, self.key)
        except AttributeError:
            pass

    @property
    def enabled(self):
        """Is syndication available for the site and a folder"""
        return self.site_settings.isAllowed \
               and ISyndicatable.providedBy(self.context)

    def enable(self):
        """Enable syndication for a folder"""
        alsoProvides(self.context, ISyndicatable)

    def disable(self):
        """Disable syndication for a folder"""
        self.revert()
        noLongerProvides(self.context, ISyndicatable)
