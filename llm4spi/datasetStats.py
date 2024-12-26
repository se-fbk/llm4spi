#
# Contain functions for obtaining the statistics of the llm4spi-compatible datasets.
#

import os
from data import ZEROSHOT_DATA, read_problems, write_jsonl
from evaluation import listSplit

def getNumOfTestCases(task:dict, type:str) -> dict :
    if not(f"{type}_condition_tests" in task) or task[f"{type}_condition_tests"] == "" :
       return { "base1":0, "base2":0, "validation":0, "all":0}
    
    splitToken = '==='
    test_cases0 = eval(task[f"{type}_condition_tests"])
    test_suites = listSplit(test_cases0,splitToken)
    if len(test_suites) == 1 :
        base1 = len(test_suites[0])
        base2 = 0
        validation = 0
    elif len(test_suites) == 2:
        base1 = len(test_suites[0])
        base2 = 0
        validation = len(test_suites[1])
    else: # so we have three suites
        base1 = len(test_suites[0])
        base2 = len(test_suites[1])
        validation = len(test_suites[2])
    all = base1 + base2 + validation
    R = { "base1":base1, "base2":base2, "validation":validation, "all":all}
    print(f">>> {task["task_id"]}: {R}")
    return R

def printStats(datafile:str):
  tasks = read_problems(datafile)
  tasks = tasks.values()
  N = len(tasks)
  numberOfPreCond  = len([ 1 for T in tasks if "pre_condition" in T and T["pre_condition"] != "" ])
  numberOfPostCond = len([ 1 for T in tasks if "post_condition" in T and T["post_condition"] != "" ])
  totNumTestCasesPreCond  = sum([ getNumOfTestCases(T,"pre")["all"] for T in tasks ])
  totNumTestCasesPostCond = sum([ getNumOfTestCases(T,"post")["all"] for T in tasks ])
  totNumBase1TestCasesPreCond  = sum([ getNumOfTestCases(T,"pre")["base1"] for T in tasks ])
  totNumBase1TestCasesPostCond = sum([ getNumOfTestCases(T,"post")["base1"] for T in tasks ])
  totNumBase2TestCasesPreCond  = sum([ getNumOfTestCases(T,"pre")["base2"] for T in tasks ]) 
  totNumBase2TestCasesPostCond = sum([ getNumOfTestCases(T,"post")["base2"] for T in tasks ]) 
  totNumValidationTestCasesPreCond  = sum([ getNumOfTestCases(T,"pre")["validation"] for T in tasks ]) 
  totNumValidationTestCasesPostCond = sum([ getNumOfTestCases(T,"post")["validation"] for T in tasks ]) 

  print("=== Stats of " + datafile)
  print(f"  * #tasks:{N}")
  print(f"  * #pre-cond:{numberOfPreCond}")
  print(f"  * #post-cond:{numberOfPostCond}")
  print( "  --")
  print(f"  * avrg #tests(all) pre-cond :{totNumTestCasesPreCond/numberOfPreCond}")
  print(f"  * avrg #base1-tests pre-cond:{totNumBase1TestCasesPreCond/numberOfPreCond}")
  print(f"  * avrg #base2-tests pre-cond:{totNumBase2TestCasesPreCond/numberOfPreCond}")
  print(f"  * avrg #validation-tests pre-cond:{totNumValidationTestCasesPreCond/numberOfPreCond}")
  print( "  --")
  print(f"  * avrg #tests(all) post-cond :{totNumTestCasesPostCond/numberOfPostCond}")
  print(f"  * avrg #base1-tests post-cond:{totNumBase1TestCasesPostCond/numberOfPostCond}")
  print(f"  * avrg #base2-tests post-cond:{totNumBase2TestCasesPostCond/numberOfPostCond}")
  print(f"  * avrg #validation-tests post-cond:{totNumValidationTestCasesPostCond/numberOfPostCond}")
  



if __name__ == '__main__':
   ROOT = os.path.dirname(os.path.abspath(__file__))
   dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")
   #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")
   printStats(dataset)
  
  
  