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
"""Search Form Schema"""

from datetime import date, timedelta

from DateTime import DateTime

from zope.interface import Interface, directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema import Choice, Int, Datetime, List, TextLine, ASCIILine
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

def status_vocab(context):
    """Provides a list of workflow states"""
    catalog = getToolByName(context, 'portal_catalog')
    values = [((u'--any--'), "None")]
    values += [(v, v) for v in catalog.uniqueValuesFor('review_state')]
    return SimpleVocabulary.fromItems(values)
directlyProvides(status_vocab, IContextSourceBinder)

def subject_vocab(context):
    """Provides a list of subject keywords"""
    catalog = getToolByName(context, 'portal_catalog')
    values = [((u'--any--'), "None")]
    values += [(v, v) for v in catalog.uniqueValuesFor('Subject')]
    return SimpleVocabulary.fromItems(values)
directlyProvides(subject_vocab, IContextSourceBinder)

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
directlyProvides(date_vocab, IContextSourceBinder)

def type_vocab(context):
    """Provides a list of portal types"""
    ttool = getToolByName(context, 'portal_types')
    types = ttool.listTypeInfo()
    terms = [SimpleTerm(None, None, '--any--')]
    terms += [SimpleTerm(t.getId(), t.getId(), t.Title()) for t in types]
    return SimpleVocabulary(terms)
directlyProvides(type_vocab, IContextSourceBinder)


class ISearchSchema(Interface):

    review_state = Choice(
                        title=(_(u"Review Status")),
                        source=status_vocab,
                        description=(_(
                            u"As a reviewer, you may search for items based on"
                            u" their review state. If you wish to constrain"
                            u" results to items in certain states, select them"
                            u" from this list.")),
                        default="None"
                        )

    search_text = TextLine(
                        title=(_(u"Full Text")),
                        description=(_(
                            u"For a simple text search, enter your search term"
                            u" here. Multiple words may be found by combining"
                            u" them with AND and OR. This will find text in"
                            u" items' contents, title and description.")),
                        required=False
                        )

    subject = Choice(
                title=(_(u"Subject")),
                description=(_(u"")),
                source=subject_vocab,
                default="None"
                )

    description = TextLine(
                    title=(_(u"Description")),
                    description=(_(
                        u"You may also search the items' descriptions and"
                        u" titles specifically. Multiple words may be found by"
                        u" combining them with AND and OR.")),
                    required=False
                    )

    when = Choice(
            title=(_(u"Find new items since...")),
            description=(_(
                u"You may find only recent items by selecting a time-frame."
                        )),
            source=date_vocab,
            default=date.today())

    portal_type = Choice(
                    title=(_(u"Item type")),
                    description=(_(
                        u"You may limit your results to particular kinds of"
                        u" items by selecting them above. To find all kinds of"
                        u" items, do not select anything.")),
                    source=type_vocab,
                    default="None")

    creator = ASCIILine(
                title=(_(u"Creator")),
                description=(_(
                    u"To find items by a particular user only, enter their"
                    u" username above. Note that you must enter their username"
                    u" exactly.")),
                required=False
                )
