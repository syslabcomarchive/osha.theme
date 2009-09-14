import re 

from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.CMFCore.utils import getToolByName

from slc.clicksearch.interfaces import IClickSearchConfiguration

class SinToolKeyVocabulary(object):
    """Vocabulary factory returning all available keys in CMFSin's 
       sin_tool.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        sin = getToolByName(site, 'sin_tool')
        items = []
        for c in sin.Channels():
            items.append(SimpleTerm(c.id, c.id, c.id))

        return SimpleVocabulary(items)

SinToolKeyVocabulary = SinToolKeyVocabulary()

class PressContactVocabulary(object):
    """Vocabulary factory returning all available keys in CMFSin's 
       sin_tool.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        cat = getToolByName(site, 'portal_catalog')
        items = []
        for c in cat(portal_type='PressContact'):
            items.append(SimpleTerm(c.id, c.getPath(), c.pretty_title_or_id))

        return SimpleVocabulary(items)

PressContactVocabulary = PressContactVocabulary()

from Products.Archetypes.interfaces._vocabulary import IVocabulary
from Products.Archetypes.atapi import DisplayList

class AnnotatableLinkListVocabulary(object):
    """Vocabulary factory returning Section names for the AnnotatableLinkList Mechanism in the Document
    """
    implements(IVocabulary)

    display_list = [
        ("authorities", "Authorities"), 
        ("social_partners", "Social Partners"),
        ("research_organisations", "Research Organisations"), 
        ("other_national", "Other National Sites"), 
        ("more", "More Related Content"),
    ]


    def getDisplayList(self, context=None):
        """ """
        site = getSite()
        # perhaps check context for some settings, otherwise return a default
        return DisplayList(self.display_list)

    def getVocabularyDict(self, instance=None):
        """ """
        d = {}
        for i in self.display_list:
            d[i[0]] = i[1]
        return d

    def isFlat(self):
        """ returns true if the underlying vocabulary is flat, otherwise
            if its hierachical (tree-like) it returns false.
        """
        return True

    def showLeafsOnly(self):
        """ returns true for flat vocabularies. In hierachical (tree-like)
            vocabularies it defines if only leafs should be displayed, or
            knots and leafs.
        """
        return True