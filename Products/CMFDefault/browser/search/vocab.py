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
"""Vocabularies for portal search form"""

from datetime import date, timedelta

from DateTime import DateTime

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import MessageFactory as _

def status_vocab(context):
    """Provides a list of workflow states"""
    catalog = getToolByName(context, 'portal_catalog')
    values = [((u'--any--'), "None")]
    values += [(v, v) for v in catalog.uniqueValuesFor('review_state')]
    return SimpleVocabulary.fromItems(values)

def subject_vocab(context):
    """Provides a list of subject keywords"""
    catalog = getToolByName(context, 'portal_catalog')
    values = [((u'--any--'), "None")]
    values += [(v, v) for v in catalog.uniqueValuesFor('Subject')]
    return SimpleVocabulary.fromItems(values)

def date_vocab(context):
    """Provides a list of dates for searching with"""
    mtool = getToolByName(context, 'portal_membership')
    dates = [SimpleTerm(date(1970, 1, 1), date(1970, 1, 1), 'Ever')]
    if not mtool.isAnonymousUser():
        login_time = mtool.getAuthenticatedMember().last_login_time
        if not hasattr(login_time, 'parts'):
            login_time = DateTime(login_time)
        login = date(*login_time.parts()[:3])
        dates.append(SimpleTerm(
            login, login, 'Last login')
                     )

    today = date.today()
    dates.append(SimpleTerm(today - timedelta(days=1),
                            today - timedelta(days=1),
                            u'Yesterday'
                            )
                 )
    dates.append(SimpleTerm(today - timedelta(days=7),
                            today - timedelta(days=7),
                            u'Last week'
                            )
                 )
    dates.append(SimpleTerm(today - timedelta(days=31),
                            today - timedelta(days=31),
                            u'Last month'
                            )
                 )
    return SimpleVocabulary(dates)

def type_vocab(context):
    """Provides a list of portal types"""
    ttool = getToolByName(context, 'portal_types')
    types = ttool.listTypeInfo()
    terms = [SimpleTerm(None, None, '--any--')]
    terms += [SimpleTerm(t.getId(), t.getId(), t.Title()) for t in types]
    return SimpleVocabulary(terms)
