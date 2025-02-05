#
# For checking that given data-set is structurally correct
#
import data
import os


def printPrograms_InDataSet(data_file: str, whichProblem:str) -> None :
   """
   Print the programs in the dataset.
   """
   problems = data.read_problems(data_file)
   if whichProblem != None :
      problems = { whichProblem : problems[whichProblem] }

   for p in problems:
      P = problems[p]
      print("")
      print(f"** Problem {p} **")
      if "program" in P:
         print("** Program:")
         print(P["program"])
      if "pre_condition_solution" in P:
         print("** Pre-cond:")
         print(P["pre_condition_solution"])
      if "post_condition_solution" in P:
         print("** Post-cond:")
         print(P["post_condition_solution"])

def checkPrePostSolutions_InDataSet(data_file: str) -> None :
   """
   Check if the pre- and post-conditions in the given data set can be
   read by Python, and then if the corresponding test-cases of these
   pre-/post-conditions can be executed without crashing.
   """
   problems = data.read_problems(data_file)
   print(f"** Checking {len(problems)} problems...")
   all_ok = True
   for p in problems:
      P = problems[p]
      problemId = p
      print(f"** Problem {problemId}:")
      
      preSolution = None

      if not ("pre_condition_solution" in P) or P["pre_condition_solution"] == "" :
         print(f"   pre-cond: none given.")

      else:
         preSolution = P["pre_condition_solution"]
         try:
            exec(preSolution,globals())
         except:
            print(f">>> OUCH pre-cond problem {p} has a problem.")
            print(preSolution)
         try:
            test_cases = [ tc for tc in eval(P["pre_condition_tests"]) if tc != "===" ]
            #print(test_cases)
            solution_results = [eval(f"check_pre_solution_{problemId}(*test_case)") for test_case in test_cases]
            print(f"   precond tests results:{solution_results}")
         except:
            print(f">>> OUCH pre-cond problem {p} has a crashing test")
            raise Exception("OUCH")

      if not ("post_condition_solution" in P):
         print(f"   post-cond: none given.")
      
      else:
         postSolution = P["post_condition_solution"]
         try:
            exec(postSolution,globals())
         except:
            print(f">>> OUCH post-cond problem {p} has a problem.")
            print(postSolution)
            raise Exception("OUCH")
         try:
            test_cases = [tc for tc in eval(P["post_condition_tests"]) if tc != "===" ]
            solution_results = [eval(f"check_post_solution_{problemId}(*test_case)") for test_case in test_cases]
            print(f"   postcond tests results:{solution_results}")
         except:
            print(f">>> OUCH post-cond problem {p} has a crashing test")
            raise Exception("OUCH")
         # comparing with the program's run, if the program is provided
         if "program" in P:
            prg = P["program"]
            try:
               exec(prg,globals())
            except:
               print(f">>> OUCH the program of problem {p} has a problem.")
               print(prg)
               raise Exception("OUCH")
            zzz = []
            for tc in test_cases:
               tc_ = tc[1:]
               if preSolution != None and not(eval(f"check_pre_solution_{problemId}(*tc_)")) :
                  verdict = 'rejected by pre-cond'
                  zzz.append(verdict)
                  continue
               retval = eval(f"Pr_{problemId}(*tc_)")
               tc_.insert(0,retval)
               verdict = eval(f"check_post_solution_{problemId}(*tc_)")
               zzz.append((retval,verdict))
            print(f"   prg-run tests results:{zzz}")
            ok = all([ r[1] for r in zzz])
            print(f"   prg-run tests all-pass: {ok}")
            all_ok = all_ok and ok
               
   print( "** Done running all tests...")
   print(f"** All prg-tests passed: {all_ok}")


def printField_InDataSet(data_file:str, id:str, idFieldName:str, fieldToPrint:str) -> None :
   for P in data.stream_jsonl(data_file) :
     if P[idFieldName] == id :
        if fieldToPrint in P :
           print(P[fieldToPrint])
           return
        else :
           print(f">>> {id} has no field {fieldToPrint}!")
   print(f">>> the data has no entry for {id}!")

if __name__ == '__main__':
   dataset = data.ZEROSHOT_DATA
   ROOT = os.path.dirname(os.path.abspath(__file__))
   dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")
   #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")
   checkPrePostSolutions_InDataSet(dataset)
   #printPrograms_InDataSet(dataset, whichProblem="5")
   #printField_InDataSet("../../llm4spiDatasets/data/humaneval-reformatted.json","HumanEval/0","task_id","prompt")
   #printField_InDataSet("../../llm4spiDatasets/data/humaneval-reformatted.json","HumanEval/0","task_id","prompt")
