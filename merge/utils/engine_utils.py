import os
import string
from django.template import Context, Engine
from django.conf import settings
from merge.config import local_root

def get_engine(config):
    engine = Engine(

        dirs=[
            os.path.join(local_root, 'templates/').replace('\\', '/'), 
            os.path.join(settings.BASE_DIR, local_root, config.tenant+'/templates/').replace('\\', '/'),],

        libraries={
                # 'relative_path': 'merge.relative_path',
                # 'mathfilters': 'merge.templatetags.mathfilters',
        },

        # add options for relative path names
        )
    return engine


def substituteVariablesPlain(config, fileNameIn, fileNameOut, subs):
    c = Context(subs)
    fileIn = open(fileNameIn, "r", encoding = "utf-8")
    fullText = fileIn.read()
    t = get_engine(config).from_string(fullText)
    xtxt = t.render(c)
    xtxt = apply_sequence(xtxt)
    fileOut = open(fileNameOut, "w", encoding="utf-8")
    fileOut.write(xtxt)
    return {"file": fileNameOut}


def substituteVariablesPlainString(config, stringIn, subs):
    c = Context(subs)
    t = get_engine(config).from_string(stringIn)
    xtxt = t.render(c)
    stringOut = apply_sequence(xtxt)
    return stringOut


def apply_sequence(text):
    alf = string.ascii_uppercase
    target = '[% #A %]'
    sub = text.find(target)
    n = 0
    while sub >= 1:
        text = text[:sub]+alf[n]+text[sub+len(target):]
        n += 1
        sub = text.find(target)
    return text



