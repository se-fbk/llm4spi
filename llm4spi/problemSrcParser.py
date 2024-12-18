#
# Functions for reading a problem-source file and extract its components.
#
from typing import Iterable, Dict
import os
import data
import json

def parseProblems(dataSetDir:str) -> Dict[str, Dict]:
    """
    Parse the problems listed inside the given data-set directory. The
    result is a dictionary D. For each problem P in the directory, D
    maps P-id to another dictionary U that contains P's components.
    """
    problemFolders = [ f for f in os.listdir(dataSetDir) if not f.startswith('.') and not f.endswith('.md') ]
    problemFolders = sorted(problemFolders)
    problems = [ parseProblem(os.path.join(dataSetDir,P, P + ".py" )) for P in problemFolders ]
    result = { P["task_id"] : P for P in problems}
    #print(result)
    return result
    
def writeProblemsAsJSONL(dataSetDir:str, outputfile:str):
    problems = parseProblems(dataSetDir)
    problems = [ problems[pid] for pid in sorted(problems.keys()) ]
    print("**")
    for P in problems:
       print("  " + P['task_id'])
    print(f"** {len(problems)}")

    with open(outputfile,'wb') as f:
        f.write((json.dumps(problems,indent=3)).encode('utf-8'))


def parseProblem(problemSrcFile:str) -> Dict :
    """
    Parse a problem's source file to get its various components, e.g. txt-descriptions,
    the pre- and post-conditions, test-inputs, etc. The result is put in a
    dictionary. 
    """
    with open(problemSrcFile) as f:
       content = f.read()
    lines = content.split('\n')

    tid = (next(r for r in lines if r.startswith("#@ task_id"))).split(':')[1]
    prg = getCode(content,"program")
    prgDesc = getTxtDesc(content,"program-desc")
    precond  = getCode(content,"pre_condition_solution")
    preCondHeader = (precond.split('\n')[0]).replace("solution_","")
    precondDesc = getTxtDesc(content,"pre_condition")
    tests0 = getCode(content,"pre_condition_tests")
    precondTestInputs = "" if tests0 == '' else tests0.split('= ')[1]
    postcond = getCode(content,"post_condition_solution")
    postCondHeader = (postcond.split('\n')[0]).replace("solution_","")
    postcondDesc = getTxtDesc(content,"post_condition")
    tests1 = getCode(content,"post_condition_tests")
    postcondTestInputs = '' if tests1 == '' else tests1.split('= ')[1]

    result = { "task_id" : tid,
               "program-desc" : prgDesc,
               "program" : prg,
               "pre_condition" : precondDesc,
               "pre_condition_incomplete" : preCondHeader,
               "pre_condition_solution" : precond,
               "pre_condition_tests" : precondTestInputs,
               "post_condition" : postcondDesc,
               "post_condition_incomplete" : postCondHeader,
               "post_condition_solution" : postcond,
               "post_condition_tests" : postcondTestInputs
            }

    #print(result)
    return result

def getCode(src:str, tag:str) -> str:
    return getFragment(src,tag,"#<", "#>")

def getTxtDesc(src:str, tag:str) -> str:
    return getFragment(src,tag,"\"\"\"@", "\"\"\"")

def getFragment(src:str, tag:str, openMarker:str, closeMarker:str) -> str:
    """
    Extract a fragment from src. This fragment consists of
    lines between a tag-open-marker and a close-marker.
    """
    lines = src.split('\n')
    tagOpen1  = openMarker + " " + tag + ":"
    tagOpen2  = openMarker + tag + ":"
    fragments = []
    foundStart = False 
    for row in lines:
        stripped_row = row.strip()
        if foundStart:
            if stripped_row.strip().startswith(closeMarker):
                break
            else:
                fragments.append(row)
        if stripped_row.startswith(tagOpen1) or stripped_row.startswith(tagOpen2):
            foundStart = True

    return ('\n'.join(fragments)).lstrip()


if __name__ == '__main__':
    # some tests
    #print(parseProblem("../../llm4spiDatasets/data/human-eval-specs/P0/P0.py"))
    #print(parseProblems("../../llm4spiDatasets/data/human-eval-specs"))

    writeProblemsAsJSONL("../../llm4spiDatasets/data/human-evalx-specs","../../llm4spiDatasets/data/HEx-compact.json")