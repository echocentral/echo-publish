from merge.steps.step import Step
from merge.utils.docx_utils import (
    preprocess_docx_template,
    substituteVariablesDocx_direct,
    postprocess_docx)
from merge.utils.engine_utils import substituteVariablesPlain

class MergeStep(Step):

    keyword = 'merge'

    def process(self, step_context, subs):
        if 'template' in self.step_spec:  # Allow "step" to override "template"
            step_context.template_name = self.step_spec['template']
        localTemplateFileName, localMergedFileName, localMergedFileNameOnly = \
                step_context.localNames()
        if self.step_spec["local_ext"] == ".docx":
            preprocess_docx_template(localTemplateFileName+self.step_spec["local_ext"], localTemplateFileName+"_"+self.step_spec["local_ext"])
            localfile = localTemplateFileName+"_"+self.step_spec["local_ext"]
            outcome = substituteVariablesDocx_direct(step_context.config, localfile, localMergedFileName+self.step_spec["local_ext"], subs)
            postprocess_docx(localMergedFileName+self.step_spec["local_ext"])
            outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+self.step_spec["local_ext"]
        else:
            outcome = substituteVariablesPlain(step_context.config, localTemplateFileName+self.step_spec["local_ext"], localMergedFileName+self.step_spec["local_ext"], subs)
            outcome["link"] = subs["site"]+"file/?name="+localMergedFileNameOnly+self.step_spec["local_ext"]

        return outcome
