import os
from merge.utils.resource_utils import get_local_dir

class Step(object):

    def __init__(self, step):
        self.step_spec = step

    def localNames(self, cwd, config, uniq, template_subfolder, template_name, output_subfolder):
        print("output_subfolder", output_subfolder)
        template_local_folder = get_local_dir("templates", config)+"/"
    #    template_local_folder = cwd+"/"+local_root+"/templates/"
        if template_subfolder:
            template_local_folder += template_subfolder+"/"
            if not os.path.exists(template_local_folder):
                os.makedirs(template_local_folder)
        localTemplateFileName = (template_local_folder+template_name.split(".")[0]).replace("//", "/")
        localMergedFileNameOnly = (template_name.split(".")[0]+'_'+uniq)
        if template_subfolder:
            localMergedFileNameOnly = template_subfolder[1:]+"/"+localMergedFileNameOnly
        localMergedFileNameOnly = localMergedFileNameOnly.replace("//","/").replace(" ","_").replace("/","-")
        local_output_folder = "output"
        if output_subfolder:
            print("output_subfolder", output_subfolder)
            local_output_folder += output_subfolder+"/"
            if not os.path.exists(local_output_folder):
                os.makedirs(local_output_folder)
        localMergedFileName = os.path.join(get_local_dir(local_output_folder, config), localMergedFileNameOnly).replace("//", "/")
    #    localMergedFileName = (cwd+"/"+local_root+"/"+local_output_folder+"/"+localMergedFileNameOnly).replace("//", "/") #for now, avoid creating output folders
        return localTemplateFileName, localMergedFileName, localMergedFileNameOnly

