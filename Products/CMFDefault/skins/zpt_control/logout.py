## Script (Python) "logout"
##title=Logout handler
##parameters=
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import getUtilityByInterfaceName

stool = getToolByName(context, 'portal_skins')
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
REQUEST = context.REQUEST

stool.clearSkinCookie()
try:
    cctool = getUtilityByInterfaceName('Products.CMFCore.interfaces.ICookieCrumbler')
    cctool.logout(REQUEST.RESPONSE)
except AttributeError:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')

return REQUEST.RESPONSE.redirect(utool() + '/logged_out')
