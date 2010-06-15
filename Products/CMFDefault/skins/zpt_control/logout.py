## Script (Python) "logout"
##title=Logout handler
##parameters=
from Products.CMFCore.utils import getToolByName

stool = getToolByName(context, 'portal_skins')
utool = getToolByName(context, 'portal_url')
REQUEST = context.REQUEST

stool.clearSkinCookie()
try:
    cctool = getToolByName(context, 'cookie_authentication')
    cctool.logout(REQUEST.RESPONSE)
except AttributeError:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')

return REQUEST.RESPONSE.redirect(utool() + '/logged_out')
