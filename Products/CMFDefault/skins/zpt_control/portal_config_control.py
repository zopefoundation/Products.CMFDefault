##parameters=**kw
##
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFDefault.utils import Message as _

ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')

if not ptool.hasProperty('default_charset'):
    ptool.manage_addProperty('default_charset', '', 'string')
if not ptool.hasProperty('email_charset'):
    ptool.manage_addProperty('email_charset', '', 'string')
if not ptool.hasProperty('enable_actionicons'):
    ptool.manage_addProperty('enable_actionicons', '', 'boolean')

kw.setdefault('enable_actionicons', False)

ptool.editProperties(kw)

return context.setStatus(True, _(u'CMF Settings changed.'))
