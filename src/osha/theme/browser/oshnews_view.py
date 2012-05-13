# -*- coding: utf-8 -*-
"""OSHA views for displaying News Items."""

import Acquisition
from DateTime import DateTime

from zope.component import getMultiAdapter

from plone.memoize import instance

from Products.ATContentTypes.interface import IATTopic
from Products.AdvancedQuery import Or, Eq, And, In, Le
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView

from osha.theme import OSHAMessageFactory as _


class OSHNewsView(BrowserView):
    """View for displaying news outside the current context within the context.
    """

    def __call__(self):
        return self.index()

    def getName(self):
        return self.__name__

    def Title(self):
        context = Acquisition.aq_inner(self.context)
        if IATTopic.providedBy(context):
            return context.Title()
        return _(u"heading_newsboard_latest_news")

    @instance.memoize
    def getResults(self):
        context = Acquisition.aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if hasattr(catalog, 'getZCatalog'):
            catalog = catalog.getZCatalog()

        # try to get query parameters from Topic (if present)
        query = hasattr(context, 'buildQuery') and context.buildQuery()
        if query:
            return catalog(query)

        # otherwise construct a query
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        oshaview = getMultiAdapter((self.context, self.request), name=u'oshaview')
        mySEP = oshaview.getCurrentSingleEntryPoint()
        kw = ''

        if mySEP:
            kw = mySEP.getProperty('keyword', '')

        queryA = Eq('portal_type', 'News Item')
        queryB = Eq('isNews', True)
        queryBoth = In('review_state', 'published') & Eq('path', navigation_root_path)
        if kw != '':
            queryBoth = queryBoth & In('Subject', kw)
        query = And(Or(queryA, queryB), queryBoth)
        return catalog.evalAdvancedQuery(query, (('Date', 'desc'),))

    def queryCatalog(self, b_size=20):
        results = self.getResults()
        b_start = self.request.get('b_start', 0)
        batch = Batch(results, b_size, int(b_start), orphan=0)
        return batch

    def getBodyText(self):
        """ returns body text of collection  if present """
        context = Acquisition.aq_base(Acquisition.aq_inner(self.context))
        text = getattr(context, 'getText', None) and context.getText() or ''
        return text

    def showLinkToNewsItem(self):
        return self.context.getProperty('show_link_to_news_item', True)


class OSHNewsLocalView(OSHNewsView):
    """Dislplay OSH news only from the local folder"""

    @instance.memoize
    def getResults(self):
        context = Acquisition.aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if hasattr(catalog, 'getZCatalog'):
            catalog = catalog.getZCatalog()

        now = DateTime()
        queryA = Eq('portal_type', 'News Item')
        queryB = Eq('isNews', True)
        queryBoth = In('review_state', 'published') & Eq('path', '/'.join(context.getPhysicalPath())) \
            & Le('effective', now)

        query = And(Or(queryA, queryB), queryBoth)
        results = catalog.evalAdvancedQuery(query, (('Date', 'desc'),))

        return results

    def Title(self):
        return self.context.Title()
