# Author: Andrew Elliott
# Copyright Revolutionary Systems 2016
# Distributed under the terms of GNU GPL v3
#
# Doc Merge flow management
#
import os
import json
import time
from .gd_resource_utils import (folder_file, folder, uploadAsGoogleDoc, uploadFile, 
    exportFile, getFile, file_content_as, gd_path_equivalent)
from .merge_utils import (substituteVariablesDocx, substituteVariablesDocx_direct, substituteVariablesPlain, substituteVariablesPlainString,
    convert_markdown, convert_pdf, convert_pdf_abiword, email_file, 
    combine_docx, combine_docx_direct, extract_regex_matches_docx,
    substituteVariablesPlainString, merge_docx_footer, merge_docx_header, preprocess_docx_template, 
    postprocess_docx, watermark_pdf, password_pdf)
from .resource_utils import (push_local_txt, push_local_txt_fullname,get_local_dir, get_local_txt_content)
from traceback import format_exc
from .config import remote_library
import pdfkit
#import weasyprint
#from xhtml2pdf import pisa

from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

# retrieve flow definition from library
def get_flow_resource(config, flow_folder, flow_file_name):
    flow_doc_id = folder_file(config, flow_folder, flow_file_name)["id"]
    doc_content = file_content_as(config, flow_doc_id)
    str_content = '{"flow":'+doc_content.decode("utf-8")+'}'
    return json.loads(str_content)["flow"]

# retrieve flow definition locally
def get_flow_local(cwd, config, flow_local_folder, flow_file_name):
    try:
        full_file_path = os.path.join(get_local_dir(flow_local_folder, config), flow_file_name)
        with open(full_file_path, "r") as flow_file:
            flow_def = flow_file.read()
            str_content = '{"flow":'+flow_def[flow_def.find("["):]+'}'
        return json.loads(str_content)["flow"]
    except FileNotFoundError:
        return None

def get_flow(cwd, config, flow_local_folder, flow_folder, flow_file_name):
    # potential pre-processing here
    flow = get_flow_local(cwd, config, flow_local_folder, flow_file_name)
    if flow == None:
        if remote_library:
            flow = get_flow_resource(config, flow_folder, flow_file_name)
        else:
            raise FileNotFoundError("'"+flow_file_name+"' was not found locally. No remote library")
    return flow

# retrieve flow definition locally
def get_template_list_local(config, template_list_local_folder, template_list_file_name, subs=None):
    try:
#        print(template_list_local_folder+template_list_file_name)
        full_name = template_list_local_folder+template_list_file_name
        full_name = full_name.replace("//", "/")
        with open(full_name, "r") as template_list_file:
            str_content = '{"template_list":'+template_list_file.read()+'}'
            if subs:
                str_content = substituteVariablesPlainString(config, str_content, subs)
        return json.loads(str_content)["template_list"]
    except FileNotFoundError:
        return None


# perform a merge operation, either using more complex docx logic, or as plain text
def process_merge(cwd, config, uniq, step, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs):
    try: #Allow "step to override template"
        localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, step["template"], output_subfolder)
    except KeyError: #No rederivation of names if no step["template"]
        pass        
    if step["local_ext"]==".docx":
        preprocess_docx_template(localTemplateFileName+step["local_ext"], localTemplateFileName+"_"+step["local_ext"])
        localfile = localTemplateFileName+"_"+step["local_ext"]
        outcome = substituteVariablesDocx_direct(config, localfile, localMergedFileName+step["local_ext"], subs)
        postprocess_docx(localMergedFileName+step["local_ext"])
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]
    else:
        outcome = substituteVariablesPlain(config, localTemplateFileName+step["local_ext"], localMergedFileName+step["local_ext"], subs)
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]

    return outcome

# Compound merge operation
def process_compound_merge(cwd, config, uniq, step, template_subfolder, template_list, output_subfolder, subs):
    template_local_folder = get_local_dir("templates", config)
#    template_local_folder = cwd+"/"+local_root+"/templates/"
    if template_subfolder:
        template_local_folder+=template_subfolder+"/"
    else:
        template_subfolder = "/"+template_list[:template_list.rfind("/")+1]
        template_local_folder+=template_subfolder
        template_list =template_list[template_list.rfind("/")+1:]
    localTemplateListFileName = template_local_folder+template_list
    local_output_folder = "output"
    localCombinedFileNameOnly = (template_subfolder[1:]+"/"+template_list.split(".")[0]).replace("//", "/")
    localCombinedFileNameOnly = localCombinedFileNameOnly.replace(" ","_").replace("/","-")
    localCombinedFileName = os.path.join(get_local_dir(local_output_folder, config), localCombinedFileNameOnly+"_"+uniq+step["local_ext"])
    print("Locally:",localCombinedFileName)
#    localCombinedFileName = cwd+"/"+local_root+"/"+local_output_folder+"/"+localCombinedFileNameOnly+"_"+uniq+step["local_ext"]
    template_list_content = get_template_list_local(config, template_local_folder, template_list, subs=subs)
    if not template_list_content:
        raise FileNotFoundError("'"+template_list+"' could not be found")
    files = template_list_content[0]["compound"]
    output_files = []
    for file_name in files:
        if file_name[0]=="-":
            output_files.append("pagebreak")
        else:
            localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, file_name, output_subfolder)
            if step["local_ext"]==".docx":
                preprocess_docx_template(localTemplateFileName+step["local_ext"], localTemplateFileName+"_"+step["local_ext"])
                outcome = substituteVariablesDocx_direct(config, localTemplateFileName+"_"+step["local_ext"], localMergedFileName+step["local_ext"], subs)
                postprocess_docx(localMergedFileName+step["local_ext"])

#                outcome = substituteVariablesDocx_direct(localTemplateFileName+"_"+step["local_ext"], localMergedFileName+step["local_ext"], subs)
                output_files.append(outcome["file"])
    outcome = combine_docx_direct(output_files, localCombinedFileName)
    outcome["link"] = subs["site"]+"/file/?name="+localCombinedFileNameOnly+"_"+uniq+step["local_ext"]
    return outcome

# perform a merge operation, either using more complex docx logic, or as plain text
def process_merge0(cwd, config, uniq, step, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs):
    try: #Allow "step to override template"
        localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, step["template"], output_subfolder)
    except KeyError: #No rederivation of names if no step["template"]
        pass        
    if step["local_ext"]==".docx":
        outcome = substituteVariablesDocx(config, localTemplateFileName+step["local_ext"], localMergedFileName+step["local_ext"], subs)
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]
    else:
        outcome = substituteVariablesPlain(config, localTemplateFileName+step["local_ext"], localMergedFileName+step["local_ext"], subs)
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]
    try:
        if step["footer"]=="true":
            merge_docx_footer(config,localMergedFileName+step["local_ext"], subs)
    except KeyError:
        pass

    try:
        if step["header"]=="true":
            merge_docx_header(localMergedFileName+step["local_ext"], subs)
    except KeyError:
        pass

    return outcome

# Compound merge operation
def process_compound_merge0(cwd, config, uniq, step, template_subfolder, template_list, output_subfolder, subs):
    template_local_folder = get_local_dir("templates", config)
#    template_local_folder = cwd+"/"+local_root+"/templates/"
    if template_subfolder:
        template_local_folder+=template_subfolder+"/"
    else:
        template_subfolder = "/"+template_list[:template_list.rfind("/")+1]
        template_local_folder+=template_subfolder
        template_list =template_list[template_list.rfind("/")+1:]
    localTemplateListFileName = template_local_folder+template_list
    local_output_folder = "output"
    localCombinedFileNameOnly = (template_subfolder[1:]+"/"+template_list.split(".")[0]).replace("//", "/")
    localCombinedFileNameOnly = localCombinedFileNameOnly.replace(" ","_").replace("/","-")
    localCombinedFileName = os.path.join(get_local_dir(local_output_folder, config), localCombinedFileNameOnly+"_"+uniq+step["local_ext"])
#    localCombinedFileName = cwd+"/"+local_root+"/"+local_output_folder+"/"+localCombinedFileNameOnly+"_"+uniq+step["local_ext"]
    template_list_content = get_template_list_local(config, template_local_folder, template_list, subs=subs)
    if not template_list_content:
        raise FileNotFoundError("'"+template_list+"' could not be found")
    files = template_list_content[0]["compound"]
    output_files = []
    for file_name in files:
        if file_name[0]=="-":
            output_files.append("pagebreak")
        else:
            localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, file_name, output_subfolder)
            if step["local_ext"]==".docx":
                outcome = substituteVariablesDocx(config, localTemplateFileName+step["local_ext"], localMergedFileName+step["local_ext"], subs)
                output_files.append(outcome["file"])
    outcome = combine_docx(output_files, localCombinedFileName)
    outcome["link"] = subs["site"]+"/file/?name="+localCombinedFileNameOnly+"_"+uniq+step["local_ext"]

    try:
        if step["footer"]=="true":
            merge_docx_footer(config, localCombinedFileName, subs)
    except KeyError:
        pass

    try:
        if step["header"]=="true":
            merge_docx_header(config, localCombinedFileName, subs)
    except KeyError:
        pass
    return outcome

# perform a download from Google drive, either as an export or getting content directly
def process_download(config, step, doc_id, doc_mimetype, localTemplateFileName, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs, password=None):
#    print("downloading")
#    print(doc_id)
#    print(doc_mimetype)
    if step["folder"]=="templates":
         localFileName = localTemplateFileName
    else:
         localFileName = localMergedFileName
    if doc_mimetype == 'application/vnd.google-apps.document':         
        outcome = exportFile(config, doc_id, localFileName+step["local_ext"], step["mimetype"])
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]
    else:
        outcome = getFile(config, doc_id, localFileName+step["local_ext"], step["mimetype"])
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+step["local_ext"]
    if password and step["local_ext"].lower() == ".pdf":
        password_pdf(localMergedFileName+".pdf", password)
        outcome["plainlink"] = outcome["link"]
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".pw.pdf"
        outcome["password"]=True
    else:
        outcome["password"]=False

    return outcome


# upload to Google drive, optionally converting to Google Drive format
def process_upload(config, step, localFileName, subfolder, upload_id):
    if subfolder:
        upload_folder = folder(subfolder, upload_id, create_if_absent=True)
        upload_id=upload_folder["id"]

    if step["convert"]=="gdoc":
        return uploadAsGoogleDoc(config, localFileName+step["local_ext"], upload_id, step["mimetype"])
    else:
        return uploadFile(config, localFileName+step["local_ext"], upload_id, step["mimetype"])




# convert markdown format to html
def process_markdown(cwd, config, step, localMergedFileName, localMergedFileNameOnly, subs):
    css_string = get_local_txt_content(cwd, config, "templates", "demo.css") #todo fix
    outcome = convert_markdown(localMergedFileName+step["local_ext"], localMergedFileName+".html", css_string=css_string)  
    outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".html"
    return outcome

# convert html to pdf
def process_html_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs):
    flavour = "pdfkit"
    try:
        if step["flavour"]=="weasyprint":
            flavour = "weasyprint"
    except KeyError:
        pass

    if flavour == "weasyprint":
        html_in = weasyprint.HTML(localMergedFileName+step["local_ext"])
        doc = html_in.write_pdf(target = localMergedFileName+".pdf")
    else:
        path_wkthmltopdf = b'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        output_dir = localMergedFileName[:localMergedFileName.rfind(os.path.sep)]
        doc = pdfkit.from_file(localMergedFileName+step["local_ext"], localMergedFileName+".pdf", configuration=config)


    outcome = {"file":localMergedFileName+".pdf"}
    outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".pdf"
    return outcome

# convert to pdf
def process_docx_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs):
    flavour = "soffice"
    try:
        if step["flavour"]=="abiword":
            flavour = "abiword"
    except KeyError:
        pass

    output_dir = localMergedFileName[:localMergedFileName.rfind(os.path.sep)]
    
    if flavour == "abiword":
        outcome = convert_pdf_abiword(localMergedFileName+step["local_ext"], localMergedFileName+".pdf", outdir=output_dir)  
    else:
        outcome = convert_pdf(localMergedFileName+step["local_ext"], localMergedFileName+".pdf", outdir=output_dir)  
    outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".pdf"
    return outcome


# convert to pdf
def process_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs, password=None):
    if step["local_ext"]==".docx":
        outcome = process_docx_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs)
    elif step["local_ext"]==".html":
        outcome = process_html_pdf(config, step, localMergedFileName, localMergedFileNameOnly, subs)
    else:
        outcome = {}
    if password:
        password_pdf(localMergedFileName+".pdf", password)
        outcome["plainlink"] = outcome["link"]
        outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".pw.pdf"
        outcome["password"]=True
    else:
        outcome["password"]=False
    return outcome

def wmark_pdf(config, step, localMergedFileName, localMergedFileNameOnly, template_subfolder, subs):
    if template_subfolder:
        watermark_name = os.path.join(get_local_dir("templates", config),template_subfolder[1:],step["watermark"])
    else:
        watermark_name = os.path.join(get_local_dir("templates", config),step["watermark"])
    if watermark_name.find("{{")>0:
        watermark_name = substituteVariablesPlainString(config, watermark_name, subs)
    watermark_pdf(localMergedFileName+".pdf", watermark_name)
    outcome = {"file":localMergedFileName+".wm.pdf"}
    outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+".wm.pdf"
    return outcome


'''
# upload to Google drive, optionally converting to Google Drive format
def process_upload(config, step, localFileName, subfolder, upload_id):
    if subfolder:
        upload_folder = folder(subfolder, upload_id, create_if_absent=True)
        upload_id=upload_folder["id"]

    if step["convert"]=="gdoc":
        return uploadAsGoogleDoc(config, localFileName+step["local_ext"], upload_id, step["mimetype"])
    else:
        return uploadFile(config, localFileName+step["local_ext"], upload_id, step["mimetype"])

'''
# push file to local
def process_payload_dump(cwd, config, step, localFileName, subs, payload=""):
    if step["type"]=="json":
        payload = json.dumps(subs, default = json_serial, indent=4, sort_keys=True)
    file_name = push_local_txt(cwd, config, step["folder"], localFileName.replace("output", step["folder"])+step["local_ext"], payload)  
    return {"file":file_name, "link":subs["site"]+"file/?name="+file_name.split("/")[-1]+"&path="+step["folder"]}
    #return {"file":file_name}


# extract text fragments using regex, output as xml (for now)
def process_extract(config, step, localFileName, subs):
    extract = extract_regex_matches_docx(localFileName+step["local_ext"], step["regex"], wrap=".xml", root_tag=step["root_tag"], child_tag=step["child_tag"])
    extract_file_name = localFileName+".xml"
    push_local_txt_fullname(extract_file_name, extract)
    return {"file":extract_file_name, "link":subs["site"]+"file/?name="+extract_file_name.split("/")[-1]+"&path="+step["folder"]}

# send email
def process_email(config, step, localFileName, you, credentials, subs):
    you = substituteVariablesPlainString(config, you, subs) #Placeholder replacement for email address
    return email_file(localFileName, step["from"], you, step["subject"], credentials) 

# push file to resource library
def process_push(cwd, config, step, localFileName, template_local_folder, subs, payload=""):
    file_name = push_local_txt(cwd, step["folder"], localFileName+step["local_ext"], payload)  
    return {"file":file_name, "link":subs["site"]+"file/?name="+file_name.split("/")[-1]+"&path="+template_local_folder}
    #return {"file":file_name}

def localNames(cwd, config, uniq, template_subfolder, template_name, output_subfolder):
    template_local_folder = get_local_dir("templates", config)+"/"
#    template_local_folder = cwd+"/"+local_root+"/templates/"
    if template_subfolder:
        template_local_folder+=template_subfolder+"/"
        if not os.path.exists(template_local_folder):
            os.makedirs(template_local_folder)
    localTemplateFileName = (template_local_folder+template_name.split(".")[0]).replace("//", "/")
    localMergedFileNameOnly = (template_name.split(".")[0]+'_'+uniq)
    if template_subfolder:
        localMergedFileNameOnly = template_subfolder[1:]+"/"+localMergedFileNameOnly
    localMergedFileNameOnly = localMergedFileNameOnly.replace("//","/").replace(" ","_").replace("/","-")
    local_output_folder = "output"
    if output_subfolder:
        local_output_folder+=output_subfolder+"/"
        if not os.path.exists(local_output_folder):
            os.makedirs(local_output_folder)
    localMergedFileName = os.path.join(get_local_dir(local_output_folder, config), localMergedFileNameOnly).replace("//", "/")
#    localMergedFileName = (cwd+"/"+local_root+"/"+local_output_folder+"/"+localMergedFileNameOnly).replace("//", "/") #for now, avoid creating output folders
    return localTemplateFileName, localMergedFileName, localMergedFileNameOnly


# Process all steps in the flow: grab the template document, construct local path names and then invoke steps in turn
def process_flow(cwd, config, flow, template_remote_folder, template_subfolder, template_name, uniq, subs, output_folder, output_subfolder, you, email_credentials, payload=None, require_template=True, password=None):
    localTemplateFileName, localMergedFileName, localMergedFileNameOnly = localNames(cwd, config, uniq, template_subfolder, template_name, output_subfolder)
    outcomes = []
    overall_outcome = {}
    doc_id = None
    overall_outcome["success"]=True
    overall_outcome["messages"]=[]
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

