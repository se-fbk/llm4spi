import json
from data import read_problems
import os.path



def exportOutLLMProposals(datasetFile:str, outputjson:str, dirToPutGeneratedPy:str):
    """
    Export all proposed pre-/post-conditions produced by an LLM to actual Python functions.
    The parameter outputjson is the name, with path, of the json-file containing the json
    output of a benchmarking run.

    The parameter datasetFile is the json file containing the dataset of problems to which
    the output belongs to.

    All proposals from LLM will be exported as Python functions, put in a single
    Python-file, with the same base-name as outputjson, But it will be placed in the
    dir specified by dirToPutGeneratedPy.
    """
    problems = read_problems(datasetFile)
    outputBaseName = os.path.basename(outputjson)
    outputBaseName = os.path.splitext(outputBaseName)[0]
    with open(outputjson, "r") as fp:
        results = json.load(fp)

    # pyfname = "proposals_" + outputBaseName + ".py"
    pyfname = "proposals.py"
    pyfname = os.path.join(dirToPutGeneratedPy, pyfname)

    with open(pyfname, "w") as fpy:

        def writeProposals(Tid:str, condTy:str, completions:list[str]):
            k = 0

            for body in completions:
                header0 = problems[Tid][f"{condTy}_condition_incomplete"]
                params = header0[header0.find("("):]
                funcHeader = f"def check_{condTy}_solution_{Tid}_{k}" + params
                if body == None or body == "":
                    body = "   raise Exception(\"No proposal can be extracted.\")\n"
                func = funcHeader + "\n" + body + "\n\n"
                fpy.write(func)
                k = k+1

        fpy.write("#\n# Generated file\n#\n\n")

        for R in results:
            Tid = R["task_id"]
            fpy.write("# ----------------------\n")
            fpy.write(f"# Proposals for {Tid}\n")
            fpy.write("# ----------------------\n\n")

            T = problems[Tid]
            # if "pre_condition_solution" in T:
            if T['pre_condition_solution'] != "":
                completions = R["pre_condition_completions"]
                writeProposals(Tid,"pre",completions)
            # if "post_condition_solution" in T:
            if T['post_condition_solution'] != "":
                completions = R["post_condition_completions"]
                writeProposals(Tid,"post",completions)


def executeLLMProposal(datasetFile:str, outputjson:str, Tid:str, condTy:str, proposalIndex:int, tc:list):
    """
    Give a test-case tc to the LLM proposal for pre/post-cond of task Tid.

    LLM proposals are read from a json-output file specified by outputjson. You also need to give
    the dataset-file.

    condTy specifies whether it is a pre- or post-condition proposal that you want to execute.
    proposalIndex specifies the proposal-index of the proposal you want to execute.

    That proposal will be grabbed from the json-file, then loaded into memory, and then the testcase tc
    is given to it to be evaluated. This results in either true or false. Or None, if something went
    wrong.

    The tc is a list of values. If the proposal is a post-condition, the first element of tc should
    represent the return value of the program that is being specified by the post-cond.
    """
    problems = read_problems(datasetFile)
    T = problems[Tid]
    fx = f"{condTy}_condition_incomplete"
    if not (fx in T) or T[fx] == None or T[fx] == "" : return None
    header0 = T[fx]
    params = header0[header0.find("("):]
    funcName = f"check_{condTy}_{Tid}_{proposalIndex}"  
    funcHeader = "def " + funcName + params

    with open(outputjson, "r") as fp:
        results = json.load(fp)
    
    for R in results:
        if R["task_id"] == Tid:
            completions = R[condTy + "_condition_completions"]
            body = completions[proposalIndex]
            if body == None or body == "" : return None
            funcDef = funcHeader + "\n" + body + "\n"
            print(funcDef)
            try :
                exec(funcDef,globals())
            except:
                print(f">>> Fail to load the definition of {proposalIndex}-th proposal of {condTy}-cond of {Tid}")
                return None
            # both work:
            #eval(f"{funcName}(*{tc})")
            r = eval(f"{funcName}(*tc)")
            return r

    return None



# example use:
if __name__ == '__main__':
   ROOT = os.path.dirname(os.path.abspath(__file__))
   dataset = os.path.join(ROOT, "..", "HEX", "HEx-compact.json")
   outputjson = os.path.join(ROOT, "results", "gemini-2.0-flash-exp_usePrgDesc_all_usePrgDesc_02_02_2025_18_20_44.json")
   odir = os.path.join(ROOT, "..", "HEX", "human-evalx-specs", "proposals")

   exportOutLLMProposals(dataset,outputjson,odir)

   # r = executeLLMProposal(dataset,outputjson,"HE1","post",0,[["()","()"],"()()"])
   # print(r)
