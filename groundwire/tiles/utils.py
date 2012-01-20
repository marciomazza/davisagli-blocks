import logging
import uuid

from urlparse import urljoin

from lxml import etree
from lxml import html

from zope.site.hooks import getSite

from plone.subrequest import subrequest

from zExceptions import NotFound

from Products.CMFCore.utils import getToolByName

headXPath = etree.XPath("/html/head")
layoutXPath = etree.XPath("/html/head/link[@rel='layout']")
headTileXPath = etree.XPath("/html/head/link[@rel='tile']")
panelXPath = etree.XPath("/html/head/link[@rel='panel']")

logger = logging.getLogger('plone.app.blocks')


def extractCharset(response, default='utf-8'):
    """Get the charset of the given response
    """

    charset = default
    if 'content-type' in response.headers:
        for item in response.headers['content-type'].split(';'):
            if item.strip().startswith('charset'):
                charset = item.split('=')[1].strip()
                break
    return charset


def resolve(url):
    """Resolve the given URL to an lxml tree.
    """
    
    resolved = resolveResource(url)
    return html.fromstring(resolved).getroottree()


def resolveResource(url):
    """Resolve the given URL to a unicode string. If the URL is an absolute
    path, it will be made relative to the Plone site root.
    """
    
    if url.startswith('/'):
        site = getSite()
        portal_url = getToolByName(site, 'portal_url')
        url = portal_url.getPortalObject().absolute_url_path() + url
    
    response = subrequest(url)
    if response.status == 404:
        raise NotFound(url)
    
    resolved = response.getBody()
    
    if isinstance(resolved, str):
        charset = extractCharset(response)
        resolved = resolved.decode(charset)
    
    if response.status != 200:
        raise RuntimeError(resolved)
    
    return resolved


def findTiles(request, tree, removeHeadLinks=False, ignoreHeadTiles=False):
    """Given a request and an lxml tree with the body, return a list of
    tuples of tile id, absolute tile href (including query string) and the
    tile placeholder node.

    If removeHeadLinks is true, tile links in the head are removed once
    complete. This is useful if we know that the tile's head will be merged
    into the rendered head anyway. In this case, the tile placeholder node 
    will be None.
    
    If ignoreHeadTiles is true, tile links in the head are ignored entirely.
    """
    
    tiles = []
    baseURL = request.getURL()

    # Find tiles in the head of the page
    if not ignoreHeadTiles or removeHeadLinks:
        for tileNode in headTileXPath(tree):
            tileHref = tileNode.get('href', None)

            if tileHref is not None:
                tileId = "__tile_%s" % uuid.uuid4()
                tileHref = urljoin(baseURL, tileHref)
            
                if removeHeadLinks:
                    tileNode.getparent().remove(tileNode)
                    tileNode = None
                
                if not ignoreHeadTiles:
                    tiles.append((tileId, tileHref, tileNode,))

    # Find tiles in the body
    for tileNode in tree.getroot().cssselect(".tile-placeholder"):
        tileId = tileNode.get('id', None)
        tileHref = tileNode.get('data-tile-href', None)

        if tileHref is not None:
            
            # If we do not have an id, generate one
            if tileId is None:
                tileId = "__tile_%s" % uuid.uuid4()
                tileNode.attrib['id'] = tileId
            
            tileHref = urljoin(baseURL, tileHref)
            tiles.append((tileId, tileHref, tileNode,))

    return tiles


def renderTiles(request, tree):
    """Find all tiles in the given response, contained in the lxml element
    tree `tree`, and insert them into the ouput.

    Assumes panel merging has already happened.
    """
    
    # Find tiles in the merged document.
    tiles = findTiles(request, tree, removeHeadLinks=True)

    root = tree.getroot()
    headNode = root.find('head')

    # Resolve each tile and place it into the tilepage body
    for tileId, tileHref, tileNode in tiles:
        
        tileTree = resolve(tileHref)

        if tileTree is not None:
            tileRoot = tileTree.getroot()

            # merge tile head into the page's head
            tileHead = tileRoot.find('head')
            if tileHead is not None:
                for tileHeadChild in tileHead:
                    headNode.append(tileHeadChild)

            if tileNode is not None:

                # clear children of the tile placeholder, but keep attributes
                oldAttrib = {}
                for attribName, attribValue in tileNode.attrib.items():
                    oldAttrib[attribName] = attribValue
                tileNode.clear()
                tileNode.attrib.update(oldAttrib)

                # insert tile target with tile body
                tileBody = tileRoot.find('body')
                if tileBody is not None:
                    tileNode.text = tileBody.text
                    for tileBodyChild in tileBody:
                        tileNode.append(tileBodyChild)

    return tree
