import os
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home
from osha.theme.config import product_globals

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')
ztc.installPackage('p4a.subtyper')
ztc.installPackage('RichDocument')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup, PloneSite

@onsetup
def setup_osha_theme():
    """Set up the additional products required for the OshaTheme Content.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the slc.publications package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import osha.theme
    zcml.load_config('configure.zcml', osha.theme)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    # It seems that files are automatically blobs, but my test won't run without this. (Plone3.1?)
    #ztc.installPackage('plone.app.blob')
    #ztc.installPackage('slc.publications')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_osha_theme()
setupPloneSite(products=['RichDocument'])

class OshaThemeTestCase(PloneTestCase):
    """Base class for integration tests for the 'OshaTheme' product.
    """

class OshaThemeFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'OshaTheme' product.
    """
    
    def loadfile(self, rel_filename):
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = StringIO(open(filename, 'r').read())
        data.filename = os.path.basename(rel_filename)
        return data

