from merge.steps.step import Step
from merge.utils.docx_utils import (
    preprocess_docx_template,
    substituteVariablesDocx_direct,
    postprocess_docx)
from merge.utils.engine_utils import substituteVariablesPlain

class MergeStep(Step):

    def process(self, cwd, config, uniq, localTemplateFileName, template_subfolder, localMergedFileName, localMergedFileNameOnly, output_subfolder, subs):
        try:  # Allow "step to override template"
            localTemplateFileName, localMergedFileName, localMergedFileNameOnly = \
                self.localNames(cwd, config, uniq, template_subfolder, self.step_spec["template"], output_subfolder)
        except KeyError:  # No rederivation of names if no step["template"]
            pass        
        if self.step_spec["local_ext"] == ".docx":
            preprocess_docx_template(localTemplateFileName+self.step_spec["local_ext"], localTemplateFileName+"_"+self.step_spec["local_ext"])
            localfile = localTemplateFileName+"_"+self.step_spec["local_ext"]
            outcome = substituteVariablesDocx_direct(config, localfile, localMergedFileName+self.step_spec["local_ext"], subs)
            postprocess_docx(localMergedFileName+self.step_spec["local_ext"])
            outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+self.step_spec["local_ext"]
        else:
            outcome = substituteVariablesPlain(config, localTemplateFileName+self.step_spec["local_ext"], localMergedFileName+self.step_spec["local_ext"], subs)
            outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+self.step_spec["local_ext"]

        return outcome
