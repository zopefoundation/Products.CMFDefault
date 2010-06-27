"""
Image view
$Id$
"""

from Products.CMFDefault.browser.utils import (
        ViewBase, memoize, decode)

class ImageView(ViewBase):

    """View for IImage.
    """

    @memoize
    @decode
    def image(self):
        return self.context.tag()