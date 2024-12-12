#
# Contain functions for performing the LLM evaluation towards the pre-/post-conditions
# tasks.
#

from typing import Dict
import textwrap
import data
from collections import Counter
import time
from func_timeout import func_timeout, FunctionTimedOut
import myconfig
import similarity

def compare_results(expected: list, predicted: list) -> str:
    """
    Returns a judgement after comparising the predicted results (results from running the function produced
    by AI) with of the expected results.

    Note: (**) the comparison can be configured (see myconfig.py) such that None as a prediction 
          will be interpreted as 'making no prediction', and will be excluded from judgement.
          However, if all predications are None, a 'failed' judgement is returned.

    Judgement:
    (1) 'accepted' if all predictions (excluding None-values) match the expected values.
    (2) 'failed' if AI solution crashed, or it produces a value that is not even a boolean,
        or if all predications are None.
    (3) 'too_weak' if for every not-None prediction p and the corresponding expected value e
                   we have e ==> p
    (4) 'too_strong' if for every not-None prediction p and the corresponding expected value e
                   we have p ==> e
    (5) 'rejected' if none of the above is the case. 

    """
    
    if myconfig.IGNORE_NONE_PREDICTION: 
        # special case (**) abobe
        # filter first the None-predictions
        zz = [ (e,p) for (e,p) in zip(expected,predicted) if p != None ]
        if len(zz) == 0:
            # if all predictions are None, we declare "fail":
            return "failed"
        # only inspect the expecteds and predictions for which the predictions are not None:
        expected   = [ e for (e,p) in zz ]
        predicted = [ p for (e,p) in zz ]

    #print(f">>> evaluated expecteds: {expected}")
    #print(f">>> evaluated predictions: {predicted}")

    if any((prediction == "failed") |  (type(prediction) != bool) for prediction in predicted):
        return "failed"
    
    if expected == predicted:
        return "accepted"
    
    any_false_negative = False
    any_false_positive = False

    for (expectation,prediction) in zip(expected,predicted):
        any_false_negative = any_false_negative or (expectation and (not prediction))
        any_false_positive = any_false_positive or ((not expectation) and prediction)
    
    if any_false_negative & any_false_positive:
        return "rejected"
    if any_false_negative:
        return "too_strong"
    if any_false_positive:
        return "too_weak"
    
    return "failed"
    

def try_check_condition(test_case, task_id, condType): # pre or post
    def runit(tc):
        result = eval(f"check_{condType}_{task_id}(*tc)")
        return result
    
    try:
        #result = eval(f"check_post_{task_id}(*test_case)")
        # run the pre/post-cond in the testcase; impose time out too:
        result = func_timeout(myconfig.RUN_SINGLE_TESTCASE_TIMEOUT, runit, args=[test_case])
    except FunctionTimedOut:
        print(">>> An AI solution execution on a test-case is killed due to timed out.")
        return "failed"
    except Exception as e:
        #print(f">>> CRASH {e}")
        return "failed"
    return result


def listSplit(s:list, sep): 
    """
    split the list s into segments which are separated by sep
    """
    segments = []
    z = []
    for x in s:
        if x==sep:
            segments.append(z)
            z = []
        else:
            z.append(x)
    segments.append(z)
    return segments

def evaluate_task_result(task: Dict, condition: str):
    """
    Given a single task, described in a dictionary, this function builds the solution 
    and predicted pre or post condition function-definitions that corresponds
    to the task. E.g. it constructs definitions 'def f1_solution...' and 'def f1_predicted...'.

    The condition argument is either 'pre' or 'post'.

    After the defs are constructred, the function evaluates the predicted 
    function's performance.

    The evaluation results are added/updated as entries in the given
    task dictionary (side-effect).
    """

    task[f"{condition}_condition_baseEvaluation"] = None
    task[f"{condition}_condition_evaluation"] = None
    task[f"{condition}_condition_baseEvaluations"] = None
    task[f"{condition}_condition_evaluations"] = None
    task[f"{condition}_condition_editDistances"] = None
    task[f"{condition}_condition_avrgRelativeEditDistance_ofUnrejected"] = None
    task[f"{condition}_condition_avrgSize_ofUnrejected"] = None
 
    # we first handle the case when the task pre- or post-condition
    # does not exists:
    if not (f"{condition}_condition" in task) : 
        return
    conditionDesc = task[f"{condition}_condition"]
    if conditionDesc==None or conditionDesc=="":
        return

    # The task pre-/post- exists, we proceed with its evaluation:

    solution_function = task[f"{condition}_condition_solution"]
    # executing the solution-function def; not expecting it to fail
    #complete_solution_function = task[f"{condition}_condition_incomplete"] + "\n" + indented_solution_function_body
    try:
        exec(solution_function,globals())
    except:
        print(">>>>>> The def of the solution function crashed!")
        print(solution_function)
        return

    # if the test-cases are marked with a split token, this indicates that
    # they consists of two groups: base-group and validation-group.
    # We separate them:
    splitToken = '==='
    test_cases0 = eval(task[f"{condition}_condition_tests"])
    test_suites = listSplit(test_cases0,splitToken)
    test_casesBase = test_suites[0]
    if len(test_suites) == 1:
        test_casesValidation = []
    elif len(test_suites) == 2:
        test_casesValidation = test_suites[1]
    else: # then we have at least three suites
        if myconfig.CONFIG_USE_SECOND_TESTSUITE_AS_BASETESTS_TOO:
            test_casesBase.extend(test_suites[1])
            test_casesValidation = []
            for suite in test_suites[2:] : test_casesValidation.extend(suite)
        else:
            test_casesValidation = []
            for suite in test_suites[1:] : test_casesValidation.extend(suite)
    
    # executing the test-cases on the solution-function, also not expecting these
    # to fail:
    if (condition == "pre"):
        solution_resultsBase = [eval(f"check_pre_solution_{task["task_id"]}(*test_case)") for test_case in test_casesBase]
        solution_resultsValidation = [eval(f"check_pre_solution_{task["task_id"]}(*test_case)") for test_case in test_casesValidation]
    else:
        solution_resultsBase = [eval(f"check_post_solution_{task["task_id"]}(*test_case)") for test_case in test_casesBase]
        solution_resultsValidation = [eval(f"check_post_solution_{task["task_id"]}(*test_case)") for test_case in test_casesValidation]

    print(f"task: {task["task_id"]}, condition: {condition}")
    print(solution_function)
    print(f"Base: {solution_resultsBase}")
    print(f"Validation: {solution_resultsValidation}")

    # get all the AI-completions, indent each one of them as well:
    AI_completions = [ textwrap.indent(body,'    ') for body in task[f"{condition}_condition_completions"] ]
    # now, evaliate each candidate-completion:
    baseEvaluationz = []
    fullEvaluationz = []
    editDistansez = []

    for k in range(len(AI_completions)):
        indented_function_body = AI_completions[k]
        complete_function = task[f"{condition}_condition_incomplete"] + "\n" + indented_function_body
        dummy_function = task[f"{condition}_condition_incomplete"] + "\n   raise(\"dummy function invoked!\")"

        editDistansez.append(similarity.levenshteinDistance(solution_function,complete_function))
        
        print(f"** running tests on candidate {k}")
    
        # executing the def. of the AI's function; it may fail (e.g. if AI's code is not even syntax correct)
        try:
            exec(dummy_function,globals())
            exec(complete_function,globals())
        except:
            print(f">>>>>> The def of completion-proposal crashed!")
            print(f">>>>>> src:\n {complete_function}")
            baseEvaluationz.append('NOT accepted')
            fullEvaluationz.append('failed')
            continue
    
        # running the test-cases on the AI's function; this may fail too:
        if (condition == "pre"):
            completion_resultsBase = [try_check_condition(test_case, task["task_id"],"pre") for test_case in test_casesBase]
            completion_resultsValidation = [try_check_condition(test_case, task["task_id"],"pre") for test_case in test_casesValidation]
        else:
            completion_resultsBase = [try_check_condition(test_case, task["task_id"],"post") for test_case in test_casesBase]
            completion_resultsValidation = [try_check_condition(test_case, task["task_id"],"post") for test_case in test_casesValidation]

        print(complete_function)

        rawBaseEvalResult = compare_results(solution_resultsBase, completion_resultsBase)
        verdictBaseTest = 'accepted' if rawBaseEvalResult == 'accepted' else 'NOT accepted'
        if test_casesValidation == []:   
          verdictFullTest = rawBaseEvalResult
        else:
          verdictFullTest = compare_results(solution_resultsBase   + solution_resultsValidation, 
                                            completion_resultsBase + completion_resultsValidation)
        baseEvaluationz.append(verdictBaseTest)
        fullEvaluationz.append(verdictFullTest)
        print(f"Base ({verdictBaseTest}): {completion_resultsBase}")
        print(f"Validation ({verdictFullTest}): {completion_resultsValidation}")
    
    task[f"{condition}_condition_baseEvaluations"] = baseEvaluationz
    task[f"{condition}_condition_evaluations"] = fullEvaluationz
    task[f"{condition}_condition_editDistances"] = editDistansez

    # calculating average edit-distance of completions which do not fail or rejected:
    editDistances2 = [  D for (v,D) in zip(baseEvaluationz,editDistansez) if v == 'accepted' or v=='too_weak' or v=='too_strong' ]
    N = len(editDistances2)
    if N>0:
        N = 0.0 + N
        task[f"{condition}_condition_avrgRelativeEditDistance_ofUnrejected"] = sum([ D['relativeDistance'] for D in editDistances2 ])/N
        task[f"{condition}_condition_avrgSize_ofUnrejected"] = sum([ D['s2Len'] for D in editDistances2 ])/N

    # We check if there is an AI-candidate solution that is accepted by the base-tests.
    # The first one of such candidate is selected. We then also validate it against
    # the whole test-suite (which include validation-tests), and report back the verdict
    # of this validation. 
    for (bVerdict,fVerdict,levDistance,k) in zip(baseEvaluationz,fullEvaluationz,editDistansez,range(len(baseEvaluationz))):
        if bVerdict == 'accepted':
            # the first candidate that is accepted by the base-tests
            task[f"{condition}_condition_baseEvaluation"] = 'accepted'
            task[f"{condition}_condition_evaluation"] = 'accepted' if fVerdict == 'accepted' else 'NOT accepted'
            task[f"{condition}_condition_accepted_completion"] = k
            task[f"{condition}_condition_accepted_completion_editDistance"] = levDistance
            return
    # all candidates fail the base-tests:
    task[f"{condition}_condition_baseEvaluation"] = 'NOT accepted'
    task[f"{condition}_condition_evaluation"] = 'NOT accepted'
    

def mk_results_summary(tasks: Dict[str,Dict]) -> tuple :

    def worker(summary,condType): # pre or post
        basetests_evaluations = [ task[condType + "_condition_baseEvaluation"] for task in tasks.values()]
        alltests_evaluations = [ task[condType + "_condition_evaluation"] for task in tasks.values()]
        basetests_evaluations = [ r for r in basetests_evaluations if r != None]
        alltests_evaluations = [ r for r in alltests_evaluations if r != None]

        counterBase = Counter(basetests_evaluations)
        counterAll  = Counter(alltests_evaluations)

        zzz = [ task[condType + "_condition_baseEvaluations"] for task in tasks.values()]
        weakAccepts = [ baseEvals for baseEvals in zzz 
                            if baseEvals != None 
                               and len([1 for v in baseEvals if v == 'accepted' or v=='too_weak' or v=='too_strong']) > 0   ]

        summary["#tasks"] = totB = counterBase.total()
        summary["accepted by base-tests"] = counterBase["accepted"]
        summary["weakly accepted by base-tests"] = len(weakAccepts)
        summary["accepted by all-tests"] = counterAll["accepted"]
        
        editDistances1 = [ task[condType + "_condition_accepted_completion_editDistance"]["relativeDistance"] 
                            for task in tasks.values() 
                            if task[condType + "_condition_baseEvaluation"] == 'accepted']
        if len(editDistances1)==0:
            editDistances1 = None
        else:
            editDistances1 = sum(editDistances1)/(0.0 + len(editDistances1))

        summary["avrg-accepted-rel-lev"] = editDistances1

        editDistances2 = [ task[condType + "_condition_avrgRelativeEditDistance_ofUnrejected"] for task in tasks.values() ]
        editDistances2 = [ d for d in editDistances2 if d != None ]
        if len(editDistances2)==0:
            editDistances2 = None
        else:
            editDistances2 = sum(editDistances2)/(0.0 + len(editDistances2))

        summary["avrg-nonRejecteds-rel-lev"] = editDistances2

        return summary
    

    return (worker({},"pre"), worker({},"post"))

def write_evaluation_summaries(precond_evaluation_summary, 
                               postcond_evaluation_summary,
                               reportfile_basename):

    def worker(summary,condType): # pre or post
        tot = summary["#tasks"]
        N1  = summary["accepted by base-tests"]
        N1b = summary["weakly accepted by base-tests"]
        N2  = summary["accepted by all-tests"]
        
        lev1 = summary["avrg-accepted-rel-lev"]
        lev2 = summary["avrg-nonRejecteds-rel-lev"]
        percent1 = 0 if tot==0 else 100*N1/tot
        percent1b = 0 if tot==0 else 100*N1b/tot
        percent2 = 0 if tot==0 else 100*N2/tot

        print(f"   ##{condType}-cond : {tot}")
        print(f"     accepted by base-tests       : {N1} ({percent1}%)")
        print(f"     weakly accepted by base-tests: {N1b} ({percent1b}%)")
        print(f"     accepted by all-tests        : {N2} ({percent2}%)")
        print(f"     avrg-accepted-rel-lev        : {lev1}")
        print(f"     avrg-nonRejecteds-rel-lev    : {lev2}")

        if reportfile_basename == None: return

        summaryfile = reportfile_basename.replace("evaluation","summary") + ".txt"

        with open(summaryfile,'a') as F:
            F.write(f"##{condType}-cond\n")
            F.write(f"  #tasks:{tot}\n")
            F.write(f"  accepted:{N1}\n")
            F.write(f"  waekly-accepted:{N1b}\n")
            F.write(f"  correct:{N2}\n")
            F.write(f"  avrg-accepted-rel-lev:{lev1}\n")
            F.write(f"  avrg-nonRejecteds-rel-lev:{lev2}\n")

    worker(precond_evaluation_summary,"pre")
    worker(postcond_evaluation_summary,"post")


def write_evaluation_report(tasks: Dict[str,Dict], reportfile_basename:str):
    
    if reportfile_basename == None: return
    reportfile = reportfile_basename + ".csv"
    with open(reportfile,'w') as f:
        
        def worker(task,baseTestsVerdict,allTestsVerdict,conditionType): # conditionType is either pre or post
            if baseTestsVerdict == None: return
            if allTestsVerdict == 'accepted':
                proposalIndex = task[conditionType + "_condition_accepted_completion"]
                D = task[conditionType + "_condition_accepted_completion_editDistance"]
                solutionLength = D["s2Len"]
                editDistance = D["distance"]
                relativeEditDistance = D["relativeDistance"]
            else:
                proposalIndex = ''
                solutionLength = ''
                editDistance = ''
                relativeEditDistance = ''

            # check if there is an AI proposal which is not rejected; is so we have at least
            # a weak-accpetance candidate:
            weak_acceptance = len([ 1 for v in task[conditionType + "_condition_baseEvaluations"] 
                                      if v=='accepted' or v=='too_weak' or v=='too_strong' ]) > 0
            
            weak_acceptance = 'accepted' if weak_acceptance else 'NOT accepted'
            
            z = f"{tId},{tId}-{conditionType},{baseTestsVerdict},{weak_acceptance},{allTestsVerdict},{proposalIndex},{solutionLength},{editDistance},{relativeEditDistance}"
            avrgLen_nonRejected = task[conditionType + "_condition_avrgSize_ofUnrejected"]
            if avrgLen_nonRejected == None: avrgLen_nonRejected = ''
            avrgRdist_nonRejected = task[conditionType + "_condition_avrgRelativeEditDistance_ofUnrejected"]
            if avrgRdist_nonRejected == None: avrgRdist_nonRejected = ''
            z = z + f",{avrgLen_nonRejected},{avrgRdist_nonRejected}\n"
            f.write(z)
        
        f.write("task-id,task,base-test-acceptance,weak-acceptance,all-test-acceptance,accepted-index,accepted-len,accepted-lev,accepted-relative-lev,nonrejecteds-avrg-len,nonrejecteds-avrg-rel-lev\n")        
        for tId in tasks:
            task = tasks[tId]
            worker(task,task["pre_condition_baseEvaluation"],task["pre_condition_evaluation"],"pre")
            worker(task,task["post_condition_baseEvaluation"],task["post_condition_evaluation"],"post")


def evaluate_tasks_results(tasks: Dict[str,Dict], reportfile_basename:str) -> tuple :
    for task in tasks:
        task_dict = tasks[task]
        evaluate_task_result(task_dict, "pre")
        evaluate_task_result(task_dict, "post")
    summaries = mk_results_summary(tasks)
    write_evaluation_report(tasks,reportfile_basename)
    write_evaluation_summaries(summaries[0],summaries[1],reportfile_basename)
    return summaries

