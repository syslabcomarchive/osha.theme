## Script (Python) "getSection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns section name (first part of URL) to the body tag
##
contentPath = context.portal_url.getRelativeContentPath(context)
if not contentPath:
    return ''
else:
    return " ".join(["section-" + "-".join(contentPath[:d+1]) for d in range(len(contentPath))]) 
