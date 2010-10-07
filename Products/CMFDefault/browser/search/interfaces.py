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

from datetime import date

from zope.interface import Interface
from zope.schema import Choice, Int, Datetime, List, TextLine, ASCIILine

from Products.CMFDefault.utils import Message as _

class ISearchSchema(Interface):

    review_state = Choice(
                        title=(_(u"Review Status")),
                        vocabulary=u"cmf.review state",
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
                vocabulary=u"cmf.subject",
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
            vocabulary=u"cmf.date",
            default=date.today())

    portal_type = Choice(
                    title=(_(u"Item type")),
                    description=(_(
                        u"You may limit your results to particular kinds of"
                        u" items by selecting them above. To find all kinds of"
                        u" items, do not select anything.")),
                    vocabulary=u"cmf.type",
                    default="None")

    creator = ASCIILine(
                title=(_(u"Creator")),
                description=(_(
                    u"To find items by a particular user only, enter their"
                    u"username above. Note that you must enter their username"
                    u"exactly.")),
                required=False
                )
