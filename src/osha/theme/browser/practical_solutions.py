from Acquisition import aq_inner, aq_parent
from Products.AdvancedQuery import In, Eq, Ge, Le, And, Or, Generic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from osha.theme.browser.dbfilter import DBFilterView


class PracticalSolutionsView(DBFilterView):
    """ View Class for the Practical Solutions page.

        Provides a link to each section based on the folder title.
        If there is an image called "section-image.png" in the folder
        it will be used too.
        """
    template = ViewPageTemplateFile('templates/practical_solutions.pt')
    template.id = "practical-solutions"

    gpawards = ''
    intro = ''
    has_section_details = False
    sections = ['useful-links',
                'risk-assessment-tools',
                'case-studies',
                'providers',
                'faqs']

    def __call__(self):
        self.request.set('disable_border', True)

        intro = getattr(self.context, 'introduction_html', None)
        if intro is None:
            self.intro = ''
        else:
            self.intro = intro.CookedBody()

        gpaward = getattr(self.context, 'good_practice_awards_html', None)
        if gpaward is None:
            self.gpaward = ''
        else:
            self.gpaward = gpaward.CookedBody()

        return self.template()


    def search_portal_types(self):
        context = self.context
        preflang = getToolByName(self.context,
                                 'portal_languages').getPreferredLanguage()
        search_portal_types = [ "OSH_Link", "RALink", "CaseStudy", "Provider", "HelpCenterFAQ"]
        query = In('portal_type', search_portal_types)\
                & In('Language', preflang)\
                & Eq('review_state','published')
        return query

    def getSectionDetails(self):
        """ Return a path to an image and a title for each of the five
            Practical Solutions sections.
            """
        context = self.context
        section_details = {}

        for section in self.sections:
            if section in context.objectIds():
                section_details[section] = {}
                # The title is taken from the local version
                section_details[section]["title"] = context[section].Title()
                canonical_section = context.getCanonical()[section]
                # The image is taken from the canonical version
                if "section-image.png" in canonical_section.objectIds():
                    section_details[section]["section_image_src"] = \
                        canonical_section["section-image.png"].absolute_url()
                self.has_section_details = True
        return section_details


class PracticalSolutionView(DBFilterView):
    """View for displaying one of the practical solution sections.

    The section heading, image and search parameters (portal_type) are derived
    from the parent folder.

    The Title of the parent folder is used as a caption under the image for the
    current section (to be consistent with the PracticalSolutionsView).
    If there is an image in that folder called 'section-image.png' it will be
    used too.
    The portal-type to search for is derived from the id of the parent
    folder.
    """

    template = ViewPageTemplateFile('templates/practical_solution.pt')
    template.id = "practical-solution"

    portal_types_map = {
            "useful-links":"OSH_Link",
            "risk-assessment-tools":"RALink",
            "case-studies":"CaseStudy",
            "providers":"Provider",
            "faqs":"HelpCenterFAQ",
            "publications": "Publication"
            }

    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()

    def has_section_image(self):
        """ Check if an image called section-image.png exists in the folder """
        context = self.context
        parent = aq_parent(aq_inner(context))
        return "section-image.png" in parent.objectIds()

    def get_i18n_database_search_heading(self):
        """ Method to get the localised heading for the database
        search box.
        """
        context = self.context
        parent = aq_parent(aq_inner(context))
        section_id = parent.getId()
        trans_tool = getToolByName(context, "translation_service")
        preflang = getToolByName(self.context,
                                 'portal_languages').getPreferredLanguage()
        # convert "useful-links" to "heading_useful_links"
        msgid = "heading_search_%s" % section_id.replace("-", "_")
        heading  = trans_tool.utranslate("osha",
                                         msgid,
                                         {},
                                         context=context,
                                         target_language=preflang,
                                         default=parent.Title())
        return heading

    def get_keyword(self):
        """ Return the first value from keywords/request or an empty string
        """
        keywords = self.request.get("keywords", "")
        keyword = ""
        if keywords:
            keyword = keywords[0]
        return keyword

    def get_search_portal_type(self):
        """ Work out the relevant search_portal_types value from the
        query string or the parent id.
        """
        context = self.context
        parent = aq_parent(aq_inner(context))
        local_search_portal_type = []
        if self.portal_types_map.has_key(parent.id):
            local_search_portal_type = self.portal_types_map[parent.id]
        search_portal_types = self.request.get('search_portal_types',
                                               local_search_portal_type)
        return search_portal_types

    def translate(self, msgid):
        context = self.context
        trans_tool = getToolByName(context, "translation_service")
        preflang = getToolByName(self.context,
                                 'portal_languages').getPreferredLanguage()
        return trans_tool.utranslate("osha",
                                         msgid,
                                         {},
                                         context=context,
                                         target_language=preflang)

    def search_types(self):
        """ Return a list of translated search types to select
        from. This overrides the DBFilterView method to remove
        Publication and select the database using
        get_search_portal_type. """

        search_portal_types = self.get_search_portal_type()
        # if all are turned off, turn them all on. Searching for
        # nothing makes no sense.
        if not search_portal_types:
            search_portal_types = ['OSH_Link', 'RALink',
                                   'CaseStudy', 'Provider',
                                   'HelpCenterFAQ']
        TYPES = [
            (self.translate("label_useful_links"), 'OSH_Link',
             'OSH_Link' in search_portal_types) ,
            (self.translate("label_risk_assessment_tools"), 'RALink',
             'RALink' in search_portal_types) ,
            (self.translate("label_case_studies"), 'CaseStudy',
             'CaseStudy' in search_portal_types) ,
            (self.translate("label_providers"), 'Provider',
             'Provider' in search_portal_types) ,
            (self.translate("FAQ"), 'HelpCenterFAQ',
             'HelpCenterFAQ' in search_portal_types) ,
                ]

        return TYPES

    def search_portal_types(self):
        """ Publications are files with the IPublicationEnhanced
        interface """
        context = self.context
        search_portal_types = self.get_search_portal_type()
        query = None
        if 'Publication' in search_portal_types:
            query = ( Eq('portal_type', 'File')\
                      & Eq('object_provides',
                         'slc.publications.interfaces.IPublicationEnhanced')
                      )
            search_portal_types.remove('Publication')
            query = Or(query, In('portal_type', search_portal_types))
        else:
            query = In('portal_type', search_portal_types)
        query = query & Eq('review_state','published')
        return query

    def has_subcategory(self, subject=''):
        """ Do we have subcategory values for the given subject?
        """
        pvt = getToolByName(self.context, 'portal_vocabularies')
        vocab = getattr(pvt, 'Subcategory', None)
        if not vocab:
            return False
        return bool(vocab.getTermByKey(subject))

    def buildQuery(self):
        """ Build the query based on the request.
        Overriding this method from DBFilter because it treats an
        empty keywords:list as a value causing nothing to be returned
        """
        context = aq_inner(self.context)
        query = self.search_portal_types()
        local_keyword = context.getProperty('keyword', '')
        keywords = self.request.get('keywords', local_keyword)
        if keywords:
            if keywords !=  ['']:
                query = query & In('Subject', keywords)

        nace = list(self.request.get('nace', ''))
        if '' in nace:
            nace.remove('')
        if nace:
            query = query & In('nace', nace)
            #query.update({'nace':nace})

        multilingual_thesaurus = list(
            self.request.get('multilingual_thesaurus', '')
            )
        if '' in multilingual_thesaurus:
            multilingual_thesaurus.remove('')
        if multilingual_thesaurus:
            query = query & In('multilingual_thesaurus', multilingual_thesaurus)
            #query.update({'multilingual_thesaurus':multilingual_thesaurus})

        preflang = getToolByName(self.context,
                                 'portal_languages').getPreferredLanguage()
        language = self.request.get('Language', preflang)
        if language:
            if language == "en":
                query = query & In('Language', (language,''))
            else:
                query = query & Eq('Language', language)

        # don't handle remoteLanguage for FAQHelpcenter items
        spt = self.get_search_portal_type()
        faq_condition = type(spt) == list and 'HelpCenterFAQ' in spt or spt == 'HelpCenterFAQ'
        getRemoteLanguage = self.request.get('getRemoteLanguage',
                                             not faq_condition and preflang
                                             or '')
        if getRemoteLanguage:
            query = query & In('getRemoteLanguage', getRemoteLanguage)
        subcategory = self.request.get('subcategory', '')
        if subcategory:
            query = query & In('subcategory', subcategory)
            #query.update({'subcategory':subcategory})

        country = self.request.get('country', '')
        if country:
            query = query & In('country', country)
            #query.update({'country':country})

        SearchableText = self.request.get('SearchableText', '')
        if SearchableText != '':
            query = query & Generic(
                'SearchableText',
                {'query': SearchableText, 'ranking_maxhits': 10000 }
                )
            #query.update({'SearchableText': {'query': SearchableText, 'ranking_maxhits': 10000 }})
        return query

    def get_link_to_english_results(self):
        """
        If the selected language is not English, then return a link to
        the equivalent search results in English
        """
        preflang = getToolByName(self.context,
                                 'portal_languages').getPreferredLanguage()
        url = ""
        if preflang != "en":
            solution = self.aq_parent.getCanonical().absolute_url()
            keywords = self.request.get("keywords", "")
            if keywords and keywords != [""]:
                keywords = keywords[0]
            url = "%s?keywords:list=%s#database_search"\
                  % (solution, keywords)
        return url
