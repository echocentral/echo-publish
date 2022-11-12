import os
import json
from merge.config import install_name, remote_library, gdrive_root, local_root, extend_path


class ResourceNotFoundError(Exception):
    pass

class ResourceManager(object):
    pass


class LocalResourceManager(ResourceManager):

    def __init__(self, local_root=local_root):
        self.local_root = local_root

    def get_working_dir(self):
        cwd = os.getcwd()
        if (cwd.find("home") >= 0 and extend_path):  
            cwd = os.path.join(cwd, install_name)
        if (cwd.find("scripts") >= 0):  
            cwd = cwd.replace("\\scripts", "")
        return cwd

    def get_local_dir(self, local, config):
        cwd = self.get_working_dir()
        if config.tenant != '.':
            local_d = os.path.join(cwd, self.local_root, config.tenant, local, '')
        else:
            local_d = os.path.join(cwd, self.local_root, local, '')
        return local_d

    def get_output_dir(self):
        return self.get_local_dir("output")

    def get_local_txt_content(self, config, data_folder, data_file):
        try:
            full_file_path = os.path.join(self.get_local_dir(data_folder, config), data_file)
            with open(full_file_path, "r", encoding="UTF-8") as file:
                return file.read()
        except FileNotFoundError:
            raise ResourceNotFoundError(f'Resource {data_file} not found in {data_folder}')

    def get_flow_spec(self, config, flow_file_name):
        return json.loads(self.get_local_txt_content(config, 'flows', flow_file_name))



