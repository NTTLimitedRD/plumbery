import os
from libcloud.utils.py3 import PY3
from libcloud.utils.py3 import u
from libcloud.utils.py3 import httplib
from libcloud.test import MockHttp
try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET


class FileFixtures(object):
    def __init__(self):
        script_dir = os.path.abspath(os.path.split(__file__)[0])
        self.root = os.path.join(script_dir, 'fixtures')

    def load(self, file):
        path = os.path.join(self.root, file)
        if os.path.exists(path):
            if PY3:
                kwargs = {'encoding': 'utf-8'}
            else:
                kwargs = {}

            with open(path, 'r', **kwargs) as fh:
                content = fh.read()
            return u(content)
        else:
            raise IOError(path)


class ComputeFileFixtures(FileFixtures):
    def __init__(self):
        super(ComputeFileFixtures, self).__init__()


class InvalidRequestError(Exception):
    def __init__(self, tag):
        super(InvalidRequestError, self).__init__("Invalid Request - %s" % tag)


class DimensionDataMockHttp(MockHttp):

    fixtures = ComputeFileFixtures()

    def _oec_0_9_myaccount_UNAUTHORIZED(self, method, url, body, headers):
        return (httplib.UNAUTHORIZED, "", {}, httplib.responses[httplib.UNAUTHORIZED])

    def _oec_0_9_myaccount(self, method, url, body, headers):
        body = self.fixtures.load('oec_0_9_myaccount.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_myaccount_INPROGRESS(self, method, url, body, headers):
        body = self.fixtures.load('oec_0_9_myaccount.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_base_image(self, method, url, body, headers):
        body = self.fixtures.load('oec_0_9_base_image.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_base_imageWithDiskSpeed(self, method, url, body, headers):
        body = self.fixtures.load('oec_0_9_base_imageWithDiskSpeed.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deployed(self, method, url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deployed.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_pendingDeploy(self, method, url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_pendingDeploy.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_datacenter(self, method, url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_datacenter.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11(self, method, url, body, headers):
        body = None
        action = url.split('?')[-1]

        if action == 'restart':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_restart.xml')
        elif action == 'shutdown':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_shutdown.xml')
        elif action == 'delete':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_delete.xml')
        elif action == 'start':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_start.xml')
        elif action == 'poweroff':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_poweroff.xml')

        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_INPROGRESS(self, method, url, body, headers):
        body = None
        action = url.split('?')[-1]

        if action == 'restart':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_restart_INPROGRESS.xml')
        elif action == 'shutdown':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_shutdown_INPROGRESS.xml')
        elif action == 'delete':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_delete_INPROGRESS.xml')
        elif action == 'start':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_start_INPROGRESS.xml')
        elif action == 'poweroff':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_11_poweroff_INPROGRESS.xml')

        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server(self, method, url, body, headers):
        body = self.fixtures.load(
            '_oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_networkWithLocation(self, method, url, body, headers):
        if method is "POST":
            request = ET.fromstring(body)
            if request.tag != "{http://oec.api.opsource.net/schemas/network}NewNetworkWithLocation":
                raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_networkWithLocation.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_4bba37be_506f_11e3_b29c_001517c4643e(self, method,
                                                                                                   url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_4bba37be_506f_11e3_b29c_001517c4643e.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1_changeSize(self, method, url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1_changeSize.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1_changeSpeed(self, method, url, body, headers):
        body = self.fixtures.load(
            'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1_changeSpeed.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1(self, method, url, body, headers):
        action = url.split('?')[-1]
        if action == 'delete':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_disk_1.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87(self, method, url, body, headers):
        if method == 'GET':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])
        if method == 'POST':
            body = self.fixtures.load(
                'oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_POST.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deleteServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deleteServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deleteServer_INPROGRESS(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deleteServer_RESOURCEBUSY.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_rebootServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}rebootServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_rebootServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_rebootServer_INPROGRESS(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}rebootServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_rebootServer_RESOURCEBUSY.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_server(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_server.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_infrastructure_datacenter(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_infrastructure_datacenter.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_updateVmwareTools(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}updateVmwareTools":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_updateVmwareTools.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_startServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}startServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_startServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_startServer_INPROGRESS(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}startServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_startServer_INPROGRESS.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_shutdownServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}shutdownServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_shutdownServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_shutdownServer_INPROGRESS(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}shutdownServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_shutdownServer_INPROGRESS.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_resetServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}resetServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_resetServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_powerOffServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}powerOffServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_powerOffServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_powerOffServer_INPROGRESS(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}powerOffServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_powerOffServer_INPROGRESS.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deployServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deployServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_deployServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_server_e75ead52_692f_4314_8725_c8a4f4d13a87(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_server_e75ead52_692f_4314_8725_c8a4f4d13a87.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deployNetworkDomain(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deployNetworkDomain":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deployNetworkDomain.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain_f14a871f_9a25_470c_aef8_51e13202e1aa(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain_f14a871f_9a25_470c_aef8_51e13202e1aa.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain_8cdfd607_f429_4df6_9352_162cfc0891be(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_networkDomain_8cdfd607_f429_4df6_9352_162cfc0891be.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editNetworkDomain(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}editNetworkDomain":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editNetworkDomain.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteNetworkDomain(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteNetworkDomain":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteNetworkDomain.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deployVlan(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deployVlan":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deployVlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_0e56433f_d808_4669_821d_812769517ff8(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_0e56433f_d808_4669_821d_812769517ff8.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editVlan(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}editVlan":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editVlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteVlan(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteVlan":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteVlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_expandVlan(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}expandVlan":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_expandVlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_addPublicIpBlock(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}addPublicIpBlock":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_addPublicIpBlock.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock_4487241a_f0ca_11e3_9315_d4bed9b167ba(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock_4487241a_f0ca_11e3_9315_d4bed9b167ba.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock_9945dc4a_bdce_11e4_8c14_b8ca3a5d9ef8(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_publicIpBlock_9945dc4a_bdce_11e4_8c14_b8ca3a5d9ef8.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_removePublicIpBlock(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}removePublicIpBlock":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_removePublicIpBlock.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_firewallRule(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_firewallRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_createFirewallRule(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}createFirewallRule":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_createFirewallRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_firewallRule_d0a20f59_77b9_4f28_a63b_e58496b73a6c(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_firewallRule_d0a20f59_77b9_4f28_a63b_e58496b73a6c.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editFirewallRule(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}editFirewallRule":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_editFirewallRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteFirewallRule(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteFirewallRule":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteFirewallRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_createNatRule(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}createNatRule":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_createNatRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_natRule(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_natRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_natRule_2187a636_7ebb_49a1_a2ff_5d617f496dce(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_natRule_2187a636_7ebb_49a1_a2ff_5d617f496dce.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteNatRule(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}deleteNatRule":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_deleteNatRule.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_addNic(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}addNic":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_addNic.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_removeNic(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}removeNic":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_removeNic.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_disableServerMonitoring(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}disableServerMonitoring":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_disableServerMonitoring.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_enableServerMonitoring(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}enableServerMonitoring":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_enableServerMonitoring.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_changeServerMonitoringPlan(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}changeServerMonitoringPlan":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_changeServerMonitoringPlan.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_image_osImage(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_image_osImage.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_image_customerImage(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_image_customerImage.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_reconfigureServer(self, method, url, body, headers):
        request = ET.fromstring(body)
        if request.tag != "{urn:didata.com:api:cloud:types}reconfigureServer":
            raise InvalidRequestError(request.tag)
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_reconfigureServer.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_55b236ad_9119_4b48_a1bb_cf5c76a7ac0f(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_0e56433f_d808_4669_821d_812769517ff8.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_7ede3b25_2222_4285_ab61_21ffb137a763(self, method, url, body, headers):
        body = self.fixtures.load(
            'caas_2_2_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_network_vlan_0e56433f_d808_4669_821d_812769517ff8.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client_type(self, method, url, body, headers):
        body = self.fixtures.load(
            '_backup_client_type.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client_storagePolicy(
            self, method, url, body, headers):
        body = self.fixtures.load(
            '_backup_client_storagePolicy.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client_schedulePolicy(
            self, method, url, body, headers):
        body = self.fixtures.load(
            '_backup_client_schedulePolicy.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client(
            self, method, url, body, headers):
        if method == 'POST':
            body = self.fixtures.load(
                '_backup_client_SUCCESS_PUT.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])
        else:
            raise ValueError("Unknown Method {0}".format(method))

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_NOCLIENT(
            self, method, url, body, headers):
        # only gets here are implemented
        # If we get any other method something has gone wrong
        assert(method == 'GET')
        body = self.fixtures.load(
            '_backup_INFO_NOCLIENT.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_DISABLED(
            self, method, url, body, headers):
        # only gets here are implemented
        # If we get any other method something has gone wrong
        assert(method == 'GET')
        body = self.fixtures.load(
            '_backup_INFO_DISABLED.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_NOJOB(
            self, method, url, body, headers):
        # only gets here are implemented
        # If we get any other method something has gone wrong
        assert(method == 'GET')
        body = self.fixtures.load(
            '_backup_INFO_NOJOB.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_DEFAULT(
            self, method, url, body, headers):
        if method != 'POST':
            raise InvalidRequestError('Only POST is accepted for this test')
        request = ET.fromstring(body)
        service_plan = request.get('servicePlan')
        if service_plan != DEFAULT_BACKUP_PLAN:
            raise InvalidRequestError('The default plan %s should have been passed in.  Not %s' % (DEFAULT_BACKUP_PLAN, service_plan))
        body = self.fixtures.load(
            '_backup_ENABLE.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup(
            self, method, url, body, headers):
        if method == 'POST':
            body = self.fixtures.load(
                '_backup_ENABLE.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])
        elif method == 'GET':
            if url.endswith('disable'):
                body = self.fixtures.load(
                    '_backup_DISABLE.xml')
                return (httplib.OK, body, {}, httplib.responses[httplib.OK])
            body = self.fixtures.load(
                '_backup_INFO.xml')
            return (httplib.OK, body, {}, httplib.responses[httplib.OK])

        else:
            raise ValueError("Unknown Method {0}".format(method))

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_EXISTS(
            self, method, url, body, headers):
        # only POSTs are implemented
        # If we get any other method something has gone wrong
        assert(method == 'POST')
        body = self.fixtures.load(
            '_backup_EXISTS.xml')
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_modify(
            self, method, url, body, headers):
        request = ET.fromstring(body)
        service_plan = request.get('servicePlan')
        if service_plan != 'Essentials':
            raise InvalidRequestError("Expected Essentials backup plan in request")
        body = self.fixtures.load('_backup_modify.xml')

        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_modify_DEFAULT(
            self, method, url, body, headers):
        request = ET.fromstring(body)
        service_plan = request.get('servicePlan')
        if service_plan != DEFAULT_BACKUP_PLAN:
            raise InvalidRequestError("Expected % backup plan in test" % DEFAULT_BACKUP_PLAN)
        body = self.fixtures.load('_backup_modify.xml')

        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client_30b1ff76_c76d_4d7c_b39d_3b72be0384c8(
            self, method, url, body, headers):
        if url.endswith('disable'):
            body = self.fixtures.load(
                ('_remove_backup_client.xml')
            )
        elif url.endswith('cancelJob'):
            body = self.fixtures.load(
                (''
                 '_backup_client_30b1ff76_c76d_4d7c_b39d_3b72be0384c8_cancelJob.xml')
            )
        else:
            raise ValueError("Unknown URL: %s" % url)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _oec_0_9_8a8f6abc_2745_4d8a_9cbc_8dabe5a7d0e4_server_e75ead52_692f_4314_8725_c8a4f4d13a87_backup_client_30b1ff76_c76d_4d7c_b39d_3b72be0384c8_FAIL(
            self, method, url, body, headers):
        if url.endswith('disable'):
            body = self.fixtures.load(
                ('_remove_backup_client_FAIL.xml')
            )
        elif url.endswith('cancelJob'):
            body = self.fixtures.load(
                (''
                 '_backup_client_30b1ff76_c76d_4d7c_b39d_3b72be0384c8_cancelJob_FAIL.xml')
            )
        else:
            raise ValueError("Unknown URL: %s" % url)
        return (httplib.BAD_REQUEST, body, {}, httplib.responses[httplib.OK])
