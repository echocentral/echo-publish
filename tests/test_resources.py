import os
from unittest import TestCase, mock
from merge.resources.resource_manager import LocalResourceManager
from merge.models import ClientConfig


class TestResources(TestCase):
    
    def fake_cwd(self):
        return os.path.join('.')

    def test_local_wd(self):
        rm = LocalResourceManager()
        cwd = rm.get_working_dir()
        self.assertEqual(cwd, 'C:\\Users\\Andrew\\Documents\\GitHub\\echo-publish')

    @mock.patch.object(LocalResourceManager, 'get_working_dir', fake_cwd)
    def test_localised_dir(self):
        rm = LocalResourceManager()
        cwd = rm.get_working_dir()
        config = ClientConfig()
        config.tenant = '.'
        ld = rm.get_local_dir('templates', config)
        self.assertEqual(ld, cwd+'\\merge\\templates\\')
        config.tenant = 'user'
        ld = rm.get_local_dir('templates', config)
        self.assertEqual(ld, cwd+'\\merge\\user\\templates\\')

    @mock.patch.object(LocalResourceManager, 'get_working_dir', fake_cwd)
    def test_local_txt_content(self):
        rm = LocalResourceManager(local_root='tests\\fixtures')
        config = ClientConfig()
        config.tenant = '.'
        txt = rm.get_local_txt_content(config, 'templates', 'SampleText01.txt')
        self.assertTrue('Plain Text File Document' in txt)
