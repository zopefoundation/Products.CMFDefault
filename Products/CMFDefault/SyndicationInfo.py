from OFS.SimpleItem import SimpleItem

from zope.interface import alsoProvides, noLongerProvides

from Products.CMFCore.interfaces import ISyndicatable
from Products.CMFCore.utils import getToolByName


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
    
    key = "_syndication_info"
    
    def __init__(self, context):
        self.context = context
    
    @property
    def site_settings(self):
        """Get site syndication tool"""
        return getToolByName(self.context, "portal_syndication")
    
    def get_info(self):
        """
        Return syndication settings for the folder or from global site
        settings if there are none for the folder
        """
        info = getattr(self.context, self.key, None)
        if info is None:
            values = {'syUpdatePeriod': self.site_settings.syUpdatePeriod,
                      'syUpdateFrequency':self.site_setting.syUpdateFrequency,
                      'syUpdateBase': self.site_settings.syUpdateBase,
                      'max_items': self.site_settings.max_items}
            return site_settings
        return info

    def set_info(self, period, frequency, base, max_items):
        """Folder has local values"""
        values = {'syUpdatePeriod': period, 'syUpdateFrequency': frequency,
                  'syUpdateBase': base, 'max_items': max_items}
        setattr(self.context, self.key, values)
    
    info = property(get_info, set_info)

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
        try:
            delattr(self.context, self.key)
        except AttributeError:
            pass
        noLongerProvides(self.context, ISyndicatable)
    

