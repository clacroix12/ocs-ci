import logging
import pytest

from ocs_ci.ocs import constants
from ocs_ci.framework.testlib import tier1, ManageTest
from tests import helpers

log = logging.getLogger(__name__)


@pytest.fixture()
def ceph_block_pool(request):
    """
    Create and return ceph block pool
    """
    def fin():
        log.info("Deleting ceph block pool %s", block_pool.name)
        block_pool.delete()

    request.addfinalizer(fin)

    log.info("Creating ceph block pool")
    block_pool = helpers.create_ceph_block_pool()
    return block_pool


@pytest.fixture()
def create_secret(request):
    """
    Factory fixture for creating secrets
    """
    secrets = []

    def fin():
        for secret in secrets:
            log.info("Deleting secret %s", secret.name)
            secret.delete()

    request.addfinalizer(fin)

    def _create_secret(interface_type):
        log.info("Creating secret with interface type %s", interface_type)
        secret = helpers.create_secret(interface_type)
        secrets.append(secret)
        return secret

    return _create_secret


@pytest.fixture()
def create_storage_class(request, ceph_block_pool, create_secret):
    """
    Factory fixture for creating storage classes
    """
    storage_classes = []

    def fin():
        for storage_class in storage_classes:
            log.info("Deleting storage class %s", storage_class.name)
            storage_class.delete()

    request.addfinalizer(fin)

    def _create_storage_class(interface_type):
        block_pool = ceph_block_pool
        secret = create_secret(interface_type)

        log.info(
            "Creating storage class with interface type %s", interface_type
        )
        interface_name = None
        if interface_type == constants.CEPHBLOCKPOOL:
            interface_name = block_pool.name
        elif interface_type == constants.CEPHFILESYSTEM:
            interface_name = helpers.get_cephfs_data_pool_name()
        storage_class = helpers.create_storage_class(
            interface_type=interface_type,
            interface_name=interface_name,
            secret_name=secret.name
        )
        storage_classes.append(storage_class)
        return storage_class

    return _create_storage_class


@pytest.fixture()
def create_pod(request):
    """
    Factory fixture for creating pods
    """
    pods = []

    def fin():
        for pod in pods:
            log.info("Deleting pod %s", pod.name)
            pod.delete()

    request.addfinalizer(fin)

    def _create_pvc(interface_type, pvc_name):
        log.info("Creating Pod with PVC %s", pvc_name)
        pod = helpers.create_pod(
            interface_type=interface_type, pvc_name=pvc_name
        )
        pods.append(pod)
        return pod

    return _create_pvc


@pytest.fixture()
def create_pvc(request, create_storage_class):
    """
    Factory fixture for creating PVCs
    """
    pvcs = []

    def fin():
        for pvc in pvcs:
            log.info("Deleting PVC %s", pvc.name)
            pvc.delete()
            assert helpers.validate_pv_delete(pvc.backed_pv)

    request.addfinalizer(fin)

    def _create_pvc(interface_type, pvc_name):
        log.info("Creating PVC %s", pvc_name)
        storage_class = create_storage_class(interface_type)
        pvc = helpers.create_pvc(
            sc_name=storage_class.name, pvc_name=pvc_name
        )
        pvcs.append(pvc)
        return pvc

    return _create_pvc


@tier1
class TestOCSBasics(ManageTest):
    @pytest.mark.polarion_id("OCS-336")
    def test_basics_rbd(self, create_pvc, create_pod):
        """
        Testing basics: secret creation,
        storage class creation,pvc and pod with rbd
        """
        pvc_name = helpers.create_unique_resource_name('test-rbd', 'pvc')
        interface_type = constants.CEPHBLOCKPOOL
        pvc = create_pvc(interface_type, pvc_name)
        if pvc.backed_pv is None:
            pvc.reload()
        create_pod(interface_type, pvc.name)

    @pytest.mark.polarion_id("OCS-346")
    def test_basics_cephfs(self, create_pvc, create_pod):
        """
        Testing basics: secret creation,
         storage class creation, pvc and pod with cephfs
        """
        pvc_name = helpers.create_unique_resource_name('test-cephfs', 'pvc')
        interface_type = constants.CEPHFILESYSTEM
        pvc = create_pvc(interface_type, pvc_name)
        create_pod(interface_type, pvc.name)
