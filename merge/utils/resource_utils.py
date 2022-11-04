import os
from merge.config import install_name, local_root, extend_path

def get_working_dir():
    cwd = os.getcwd()
    if (cwd.find("home") >= 0 and extend_path):  
        cwd = os.path.join(cwd,install_name)
    if (cwd.find("scripts") >= 0):  
        cwd = cwd.replace("\scripts","")
    return cwd

def get_local_dir(local, config):
    cwd = get_working_dir()
    if config.tenant == '.':
        local_d = os.path.join(cwd, local_root, local)
    else:
        local_d = os.path.join(cwd, local_root, config.tenant, local)
#        local_d = "C:\\Users\\Andrew\\Documents\\GitHub\\"+install_name+"\\"+local_root+"\\"+local
    return local_d
