import os
from merge.utils.resource_utils import get_local_dir

class Step(object):

    def __init__(self, step):
        self.step_spec = step

    def localNames(self, step_context):
        template_local_folder = get_local_dir(step_context.template_folder, step_context.config)+"/"
        if step_context.template_subfolder:
            template_local_folder += step_context.template_subfolder+"/"
            if not os.path.exists(template_local_folder):
                os.makedirs(template_local_folder)
        localTemplateFileName = (template_local_folder+step_context.template_name.split(".")[0]).replace("//", "/")
        localMergedFileNameOnly = (step_context.template_name.split(".")[0]+'_'+step_context.uniq)
        if step_context.template_subfolder:
            localMergedFileNameOnly = step_context.template_subfolder[1:]+"/"+localMergedFileNameOnly
        localMergedFileNameOnly = localMergedFileNameOnly.replace("//","/").replace(" ","_").replace("/","-")
        local_output_folder = step_context.output_folder
        if step_context.output_subfolder:
            local_output_folder += step_context.output_subfolder+"/"
            if not os.path.exists(local_output_folder):
                os.makedirs(local_output_folder)
        local_split = get_local_dir(local_output_folder, step_context.config).split('\\')
        localMergedFileName = '/'.join(local_split+[localMergedFileNameOnly])
    #    localMergedFileName = (cwd+"/"+local_root+"/"+local_output_folder+"/"+localMergedFileNameOnly).replace("//", "/") #for now, avoid creating output folders
        return localTemplateFileName, localMergedFileName, localMergedFileNameOnly

