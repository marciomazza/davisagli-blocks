from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class Layer(PloneSandboxLayer):
    
    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        import groundwire.tiles
        self.loadZCML(package=groundwire.tiles)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'groundwire.tiles:default')


FIXTURE = Layer()
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE,), name='groundwire.tiles:Integration')
FUNCTIONAL_TESTING = FunctionalTesting(bases=(FIXTURE,), name='groundwire.tiles:Functional')
