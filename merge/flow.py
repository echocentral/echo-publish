# Author: Andrew Elliott
# Copyright Echo Central Ventures 2022
# Distributed under the terms of GNU GPL v3
#
# Doc Merge flow management
#
import os
import json
import time
from traceback import format_exc
from merge.steps.step import Step
from merge.utils.resource_utils import get_local_dir


class StepContext(object):

    def __init__(self, cwd, config, template_remote_folder, template_folder, template_subfolder, template_name, uniq, output_folder, output_subfolder):
        self.cwd = cwd
        self.config = config
        self.template_remote_folder = template_remote_folder
        self.template_folder = template_folder
        self.template_subfolder = template_subfolder
        self.template_name = template_name
        self.uniq = uniq
        self.output_folder = output_folder
        self.output_subfolder = output_subfolder

    def localNames(step_context):
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




class Flow(object):
    outcomes = []
    overall_outcome = {}
    doc_id = None
    overall_outcome["success"]=True
    overall_outcome["messages"]=[]

    def __init__(self, flow_spec, step_context):
        self.flow_spec = flow_spec
        self.context = step_context

    def process(self, subs, payload=None, require_template=True, password=None):
        step_dict = Step.step_dict()

        localTemplateFileName, localMergedFileName, localMergedFileNameOnly = \
            self.context.localNames()
        step_time = time.time()
        for step in self.flow_spec:
            try:
                try:
                    local_folder = step["folder"]
                except:
                    local_folder = self.context.output_folder

                if step["step"] == "merge":
                    step_class = step_dict[step["step"]]
                    step_instance = step_class(step)
                    outcome = step_instance.process(self.context, subs)

                step_end_time = time.time()
                self.outcomes.append({"step":step["name"], "success": True, "outcome":outcome, "time": step_end_time-step_time})
                step_time = step_end_time
                for key in outcome.keys():
                    if key in ["link", "id", "mimeType", "plainlink"]:
                        self.overall_outcome[key] = outcome[key]
                        self.overall_outcome[key+"_"+step["name"].replace(" ","_")]=outcome[key]
            except Exception as ex:
                step_end_time = time.time()
                self.outcomes.append({"step": step["name"], "success": False, "outcome": {"exception":str(ex)}, "time": step_end_time-step_time})
                step_time = step_end_time
                self.overall_outcome["success"] = False
                self.overall_outcome["messages"].append("Exception in step: "+step["name"]+".  "+str(ex))
                self.overall_outcome["traceback"] = format_exc(8)
                if not("critical" in step.keys() and step["critical"]=="false"):
                    break
    #                raise ex
            
    #    overall_outcome["success"]=True
        self.overall_outcome["steps"] = self.outcomes

        """
        input = {
            "cwd":cwd,
            "flow":flow,
            "template_remote_folder":template_remote_folder,
            "template_subfolder":template_subfolder,
            "template_name":template_name,
            "uniq":uniq,
    #        "subs":subs,
            "output_folder":output_folder,
            "output_subfolder":output_subfolder,
    #        "you":you,
    #        "email_credentials":email_credentials,
    #        "payload":payload,
            "require_template":require_template,
        }
        request_record = {"record": {"time": datetime.now(),"request":input, "outcome":overall_outcome}}
        request_record_str = json.dumps(request_record, default = json_serial, indent=True)
        if overall_outcome["success"]:
            state = "success"
        else:
            state="fail"
        push_local_txt(cwd, config, "requests", localMergedFileNameOnly+"."+state+".json", request_record_str)
        """
        return self.overall_outcome


