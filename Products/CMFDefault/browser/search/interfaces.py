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
"""Search Form Schema.
"""

from datetime import date
from datetime import timedelta

from DateTime import DateTime
from zope.component import getUtility
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Choice
from zope.schema import List
from zope.schema import TextLine
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFDefault.utils import Message as _

def status_vocab(context):
    """Provides a list of workflow states"""
    ctool = getUtility(ICatalogTool)
    values = [SimpleTerm(None, None, _(u"-- any --"))]
    values += [SimpleTerm(v, v, v)
               for v in ctool.uniqueValuesFor('review_state')]
    return SimpleVocabulary(values)
directlyProvides(status_vocab, IContextSourceBinder)

def subject_vocab(context):
    """Provides a list of subject keywords"""
    ctool = getUtility(ICatalogTool)
    values = [SimpleTerm(None, None, _(u"-- any --"))]
    values += [SimpleTerm(v, v, v)
               for v in ctool.uniqueValuesFor('Subject')]
    return SimpleVocabulary(values)
directlyProvides(subject_vocab, IContextSourceBinder)

def date_vocab(context):
    """Provides a list of dates for searching with"""
    mtool = getUtility(IMembershipTool)
    dates = [SimpleTerm(date(1970, 1, 1), date(1970, 1, 1), _(u'Ever'))]
    if not mtool.isAnonymousUser():
        member = mtool.getAuthenticatedMember()
        login_time = member.getProperty('last_login_time')
        if not hasattr(login_time, 'parts'):
            login_time = DateTime(login_time)
        login = date(*login_time.parts()[:3])
        dates.append(SimpleTerm(
            login, login, _(u'Last login'))
                     )

    today = date.today()
    dates.append(SimpleTerm(today - timedelta(days=1),
                            today - timedelta(days=1),
                            _(u'Yesterday')
                            )
                 )
    dates.append(SimpleTerm(today - timedelta(days=7),
                            today - timedelta(days=7),
                            _(u'Last week')
                            )
                 )
    dates.append(SimpleTerm(today - timedelta(days=31),
                            today - timedelta(days=31),
                            _(u'Last month')
                            )
                 )
    return SimpleVocabulary(dates)
directlyProvides(date_vocab, IContextSourceBinder)

def type_vocab(context):
    """Provides a list of portal types"""
    ttool =  getUtility(ITypesTool)
    types = ttool.listTypeInfo()
    terms = [SimpleTerm(None, None, _(u"-- any --"))]
    terms += [SimpleTerm(t.getId(), t.getId(), t.Title()) for t in types]
    return SimpleVocabulary(terms)
directlyProvides(type_vocab, IContextSourceBinder)


class ISearchSchema(Interface):

    review_state = List(
                        title=_(u"Review Status"),
                        description=_(
                            u"As a reviewer, you may search for items based on"
                            u" their review state. If you wish to constrain"
                            u" results to items in certain states, select them"
                            u" from this list."),
                        value_type=Choice(
                            source=status_vocab
                            ),
                        required=False,
                        )

    SearchableText = TextLine(
                    title=_(u"Full Text"),
                    description=_(
                        u"For a simple text search, enter your search term"
                        u" here. Multiple words may be found by combining them"
                        u" with AND and OR. This will find text in items'"
                        u" contents, title and description."),
                    required=False
                    )

    Title = TextLine(
                title=_(u"Title"),
                required=False
                )

    Subject = List(
                title=_(u"Subject"),
                description=_(u""),
                value_type=Choice(
                    source=subject_vocab
                    ),
                required=False
                )

    Description = TextLine(
                    title=_(u"Description"),
                    description=_(
                        u"You may also search the items' descriptions and"
                        u" titles specifically. Multiple words may be found by"
                        u" combining them with AND and OR."),
                    required=False
                    )

    created = Choice(
            title=_(u"Find new items since..."),
            description=(_(
                u"You may find only recent items by selecting a time-frame."
                        )),
            source=date_vocab,
            default=date.today()
            )

    portal_type = List(
                    title=_(u"Item type"),
                    description=_(
                        u"You may limit your results to particular kinds of"
                        u" items by selecting them above. To find all kinds of"
                        u" items, do not select anything."),
                    value_type=Choice(
                        source=type_vocab,
                        ),
                    required=False,
                    )

    listCreators = ASCIILine(
                title=_(u"Creator"),
                description=_(
                    u"To find items by a particular user only, enter their"
                    u" username above. Note that you must enter their username"
                    u" exactly."),
                required=False
                )
