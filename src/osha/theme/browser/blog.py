from Products.Five.browser import BrowserView
from plone import api


class BlogView(BrowserView):
    """View that displays a list of blog entries."""

    def __call__(self):
        return self.index()

    def get_blog_items(self):
        """Return a list of blog items. If blog entry is not available in
        currently selected language, use the canonical version ('en').

        :returns: a list of 'Blog Entry' objects
        """
        catalog = api.portal.get_tool('portal_catalog')
        blog_en = self.context.getCanonical()
        path = '/'.join(blog_en.getPhysicalPath())
        items_en = catalog(
            portal_type=['Blog Entry'],
            Language='all',
            path={"query": path, "depth": 2},
            sort_on='effective',
            sort_order='descending'
        )

        results = []
        for item in items_en:
            obj = item.getObject()
            obj_translation = obj.getTranslation()

            if obj_translation:
                results.append(obj_translation)
            else:
                results.append(obj)

        return results
