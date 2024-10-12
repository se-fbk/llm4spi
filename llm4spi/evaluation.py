from typing import Dict
import textwrap
import data
from collections import Counter


def compare_results(expected: list, predicted: list) -> str:
    """
    Returns acception state after comparison of the expected results and the actual predicted results
    """
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


def evaluate_task_result(task: Dict, condition: str):
    """
    Builds the solution and predicted pre or post condition function definition of a single task,
    based on the condition argument,
    evaluates the predicted function's performance,
    and alters the evaluation item of the task dictionary.
    """
    solution_function = task[f"{condition}_condition_solution"]

    # executing the solution-function def; not expecting it to fail
    #complete_solution_function = task[f"{condition}_condition_incomplete"] + "\n" + indented_solution_function_body
    try:
        exec(solution_function,globals())
    except:
        print(">>>>>>")
        print(solution_function)

    test_cases = task[f"{condition}_condition_tests"]
    test_cases = [ data.prepTestCase(tc) for tc in test_cases ]

    # executing the test-cases on the solution-function, also not expecting these
    # to fail:
    if (condition == "pre"):
        solution_results = [eval(f"check_pre_solution_{task["task_id"]}(*test_case)") for test_case in test_cases]
    else:
        solution_results = [eval(f"check_post_solution_{task["task_id"]}(*test_case)") for test_case in test_cases]

    print(f"task: {task["task_id"]}, condition: {condition}")
    print(solution_function)
    print(solution_results)

    indented_function_body = textwrap.indent(task[f"{condition}_condition_completion"],'    ')
    complete_function = task[f"{condition}_condition_incomplete"] + "\n" + indented_function_body
    
    # executing the def. of the AI's function; it may fail (e.g. if AI's code is not even syntax correct)
    try:
        exec(complete_function,globals())
    except:
        task[f"{condition}_condition_evaluation"] = "failed"
    
    # running the test-cases on the AI's function; this may fail too:
    if (condition == "pre"):
        completion_results = [try_check_pre(test_case, task["task_id"]) for test_case in test_cases]
    else:
        completion_results = [try_check_post(test_case, task["task_id"]) for test_case in test_cases]

    print(complete_function)
    print(completion_results)

    task[f"{condition}_condition_evaluation"] = compare_results(solution_results, completion_results)


def print_acceptance_rate(tasks: Dict[str,Dict]):
    total = len(tasks)

    pre_condition_evaluations = [tasks[task]["pre_condition_evaluation"] for task in tasks]
    post_condition_evaluations = [tasks[task]["post_condition_evaluation"] for task in tasks]
    all_evaluations = pre_condition_evaluations + post_condition_evaluations

    counter = Counter(all_evaluations)
    total = counter.total()

    print("** Evaluation result:")
    print(f"   N = {total}")
    for (state, count) in counter.items():
        print(f"   {state}: {count} ({count/total*100}%)")


def evaluate_task_results(tasks: Dict[str,Dict]) -> None:
    for task in tasks:
        task_dict = tasks[task]
        evaluate_task_result(task_dict, "pre")
        evaluate_task_result(task_dict, "post")

    print_acceptance_rate(tasks)