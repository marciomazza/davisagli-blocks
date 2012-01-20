from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
_ = MessageFactory('groundwire.tiles')

# Monkey patch for backwards-compatibility with our slightly
# different tile placeholder format.
import plone.app.blocks.utils
from lxml import etree
plone.app.blocks.utils.tileAttrib = 'data-tile-href'
plone.app.blocks.utils.bodyTileXPath = etree.XPath("/html/body//*[@data-tile-href]")
