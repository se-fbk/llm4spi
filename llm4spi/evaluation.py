#
# Contain functions for performing the LLM evaluation towards the pre-/post-conditions
# tasks.
#

from typing import Dict
import textwrap
import data
from collections import Counter
import myconfig
import similarity

def compare_results(expected: list, predicted: list) -> str:
    """
    Returns a judgement after comparising the predicted results (results from running the function produced
    by AI) with of the expected results.
    Note: None as a prediction will be interpreted as 'making no prediction', and
          will be excluded from judgement.
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
    

def try_check_pre(test_case, task_id):
    try:
        result = eval(f"check_pre_{task_id}(*test_case)")
    except:
        return "failed"
    return result


def try_check_post(test_case, task_id):
    try:
        result = eval(f"check_post_{task_id}(*test_case)")
    except:
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

    # we first handle the case when the task pre- or post-condition
    # does not exists:
    task[f"{condition}_condition_baseEvaluation"] = None
    task[f"{condition}_condition_evaluation"] = None
    task[f"{condition}_condition_baseEvaluations"] = None
    task[f"{condition}_condition_evaluations"] = None
    task[f"{condition}_condition_editDistances"] = None
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
            completion_resultsBase = [try_check_pre(test_case, task["task_id"]) for test_case in test_casesBase]
            completion_resultsValidation = [try_check_pre(test_case, task["task_id"]) for test_case in test_casesValidation]
        else:
            completion_resultsBase = [try_check_post(test_case, task["task_id"]) for test_case in test_casesBase]
            completion_resultsValidation = [try_check_post(test_case, task["task_id"]) for test_case in test_casesValidation]

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
    task[f"{condition}_condition_avrgRelativeEditDistance_ofUnrejected"] = None
    task[f"{condition}_condition_avrgSize_ofUnrejected"] = None
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
    
def print_acceptance_rate(tasks: Dict[str,Dict]):


    """
    editDistances1 = [ task["pre_condition_accepted_completion_editDistance"]["relativeDistance"] 
                            for task in tasks.values() 
                            if task["pre_condition_baseEvaluation"] == 'accepted']
    if len(editDistances1)==0:
        editDistances1 = None
    else:
        editDistances1 = sum(editDistances1)/(0.0 + len(editDistances1))
    
    editDistances2 = [ task["pre_condition_avrgRelativeEditDistance_ofUnrejected"]
                            for task in tasks.values() 
                            if task["pre_condition_avrgRelativeEditDistance_ofUnrejected"] != None ]
    if len(editDistances2)==0:
        editDistances2 = None
    else:
        editDistances2 = sum(editDistances2)/(0.0 + len(editDistances2))
    """

    def worker(condType): # pre or post
        basetests_evaluations = [ task[condType + "_condition_baseEvaluation"] for task in tasks.values()]
        alltests_evaluations = [ task[condType + "_condition_evaluation"] for task in tasks.values()]
        basetests_evaluations = [ r for r in basetests_evaluations if r != None]
        alltests_evaluations = [ r for r in alltests_evaluations if r != None]

        counterBase = Counter(basetests_evaluations)
        counterAll  = Counter(alltests_evaluations)

        totB = counterBase.total()
        print(f"   #{condType}-cond checked with base-tests = {totB}")
        N1 = counterBase["accepted"]
        percent1 = 0 if totB==0 else 100*N1/totB
        print(f"   accepted: {N1} ({percent1}%)")
        N2 = counterBase["NOT accepted"]
        percent2 = 0 if totB==0 else 100*N2/totB
        print(f"   NOT accepted: {N2} ({percent2}%)")
    
        totA = counterAll.total()
        print(f"   #{condType}-cond checked with all-tests = {totA}")
        N3 = counterAll["accepted"]
        percent3 = 0 if totA==0 else 100*N3/totA
        print(f"   accepted: {N3} ({percent3}%)")
        N4 = counterAll["NOT accepted"]
        percent4 = 0 if totA==0 else 100*N4/totA
        print(f"   NOT accepted: {N4} ({percent4}%)")


def write_evaluation_report(tasks: Dict[str,Dict], reportfile:str):
    
    if reportfile == None: return

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
            z = f"{tId},{tId}-{conditionType},{baseTestsVerdict},{allTestsVerdict},{proposalIndex},{solutionLength},{editDistance},{relativeEditDistance}"
            avrgLen_nonRejected = task[conditionType + "_condition_avrgSize_ofUnrejected"]
            if avrgLen_nonRejected == None: avrgLen_nonRejected = ''
            avrgRdist_nonRejected = task[conditionType + "_condition_avrgRelativeEditDistance_ofUnrejected"]
            if avrgRdist_nonRejected == None: avrgRdist_nonRejected = ''
            z = z + f",{avrgLen_nonRejected},{avrgRdist_nonRejected}\n"
            f.write(z)
        
        f.write("task-id,task,base-test,all-test,accepted-index,accepted-len,accepted-lev,accepted-relative-lev,nonrejecteds-avrg-len,nonrejecteds-avrg-rel-lev\n")        
        for tId in tasks:
            task = tasks[tId]
            worker(task,task["pre_condition_baseEvaluation"],task["pre_condition_evaluation"],"pre")
            worker(task,task["post_condition_baseEvaluation"],task["post_condition_evaluation"],"post")


def evaluate_tasks_results(tasks: Dict[str,Dict], reportfile_basename:str) -> None:
    for task in tasks:
        task_dict = tasks[task]
        evaluate_task_result(task_dict, "pre")
        evaluate_task_result(task_dict, "post")

    if reportfile_basename != None:
        write_evaluation_report(tasks,reportfile_basename + ".csv")

    print_acceptance_rate(tasks)

