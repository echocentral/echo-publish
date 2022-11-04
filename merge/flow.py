# Author: Andrew Elliott
# Copyright Echo Central Ventures 2022
# Distributed under the terms of GNU GPL v3
#
# Doc Merge flow management
#
import os
import json
import time


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
        print(self.template_name)


class Flow(object):
    outcomes = []
    overall_outcome = {}
    doc_id = None
    overall_outcome["success"]=True
    overall_outcome["messages"]=[]

    def __init__(self, flow_spec, context):
        self.flow_spec = flow_spec
        self.context = context

    def process(self, subs, payload=None, require_template=True, password=None):
        localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, template_name, output_subfolder)
        step_time = time.time()
        for step in flow:
            try:
                try:
                    local_folder = step["folder"]
                except:
                    local_folder = output_folder

                if step["step"]=="download":
                    if doc_id ==None and require_template:
                        if template_subfolder:
                            local_folder = local_folder+template_subfolder
                        #else:
                        #    local_folder = template_remote_folder
                        download_folder = gd_path_equivalent(config, local_folder.replace("\\","/"))
                        doc = folder_file(config, download_folder, template_name)
                        doc_id = doc["id"]
                        doc_mimetype = doc["mimeType"]
                    outcome = process_download(config, step, doc_id, doc_mimetype, localTemplateFileName, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs, password=password)

                if step["step"]=="merge":
                    outcome = process_merge(cwd, config, uniq, step, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs)

                if step["step"]=="compound_merge": #template_name is a list of template names in a json file
                    outcome = process_compound_merge(cwd, config, uniq, step, template_subfolder, template_name, output_subfolder, subs)

                if step["step"]=="merge2":
                    outcome = process_merge(cwd, config, uniq, step, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs)

                if step["step"]=="compound_merge2": #template_name is a list of template names in a json file
                    outcome = process_compound_merge(cwd, config, uniq, step, template_subfolder, template_name, output_subfolder, subs)

                if step["step"]=="merge0":
                    outcome = process_merge0(cwd, config, uniq, step, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs)

                if step["step"]=="compound_merge0": #template_name is a list of template names in a json file
                    outcome = process_compound_merge0(cwd, config, uniq, step, template_subfolder, template_name, output_subfolder, subs)

                if step["step"]=="markdown":
                    outcome = process_markdown(cwd, config, step, localMergedFileName, localMergedFileNameOnly, subs)

                if step["step"]=="pdf":
                    outcome = process_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs, password=password)

                if step["step"]=="watermark_pdf":
                    outcome = wmark_pdf(config, step, localMergedFileName, localMergedFileNameOnly, template_subfolder, subs)

                if step["step"]=="upload":
                    if local_folder=="templates":
                        localFileName = localTemplateFileName
                        upload_id = folder(config, template_remote_folder)["id"]
                        upload_subfolder = template_subfolder
                    else:
                        localFileName = localMergedFileName
                        if output_folder==None:
                            output_folder = "output"
                        output_folder = gd_path_equivalent(config, output_folder)
                        upload_id = folder(config, output_folder)["id"]
                        upload_subfolder = None
                    outcome = process_upload(config, step, localFileName, upload_subfolder, upload_id)
                    doc_id = outcome["id"]
                    doc_mimetype = outcome["mimeType"]

                if step["step"]=="email":
                    outcome = process_email(config, step, localMergedFileName, you, email_credentials, subs)

                if step["step"]=="push":
                    outcome = process_push(cwd, config, step, localTemplateFileName, "templates/"+template_subfolder+"/", subs, payload=payload)

                if step["step"]=="payload":
                    outcome = process_payload_dump(cwd, config, step, localMergedFileName, subs, payload=payload)

                if step["step"]=="extract":
                    outcome = process_extract(config, step, localMergedFileName, subs)

                step_end_time = time.time()
                outcomes.append({"step":step["name"], "success": True, "outcome":outcome, "time": step_end_time-step_time})
                step_time = step_end_time
                for key in outcome.keys():
                    if key in ["link", "id", "mimeType", "plainlink"]:
                        overall_outcome[key]=outcome[key]
                        overall_outcome[key+"_"+step["name"].replace(" ","_")]=outcome[key]
            except Exception as ex:
                step_end_time = time.time()
                outcomes.append({"step":step["name"], "success": False, "outcome": {"exception":str(ex)}, "time": step_end_time-step_time})
                step_time = step_end_time
                overall_outcome["success"]=False
                overall_outcome["messages"].append("Exception in step: "+step["name"]+".  "+str(ex))
                overall_outcome["traceback"]=format_exc(8)
                if not("critical" in step.keys() and step["critical"]=="false"):
                    break
    #                raise ex
            
    #    overall_outcome["success"]=True
        overall_outcome["steps"]=outcomes

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

        return overall_outcome


