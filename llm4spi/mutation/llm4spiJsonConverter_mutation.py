#
# For converting problems that are originally formulated in the llm4spi json format
# to individual Pyhton-script per problem.
#
import os
import json

SUITE_TO_USE = "validation"
WHAT_TO_TEST = "PROGRAM"

def generatePythons(jsonFile:str, targetDir:str):
    with open(jsonFile, "r") as fp:
        src = json.load(fp)
        tasks = [ task for  task in src ]

    k = 0
    for T in tasks:
        tid = T["task_id"]
        print(f">>> {tid}")
        taskDir = os.path.join(targetDir,tid)
        initPyFile = os.path.join(targetDir,tid, "__init__.py")
        taskPyFile = os.path.join(targetDir,tid, tid + ".py")
        testPyFile = os.path.join(targetDir,tid, "test_" + tid + ".py")
        os.makedirs(taskDir, exist_ok=True)

        with open(initPyFile, 'w') as F:
            F.write("")

        with open(taskPyFile, 'w') as F:

            F.write(f"#@ task_id:{tid}\n")

            # Prg-desc:
            F.write(f"# This is a generated file.\n\n")
            F.write(f"\"\"\"@ program-desc:\n")
            F.write(f"{T['program-desc']}\n")
            F.write("\"\"\"\n\n")

            if WHAT_TO_TEST == "PROGRAM":
                # solution-prg:
                F.write("#< program:\n")
                F.write(f"{T['program']}\n")
                F.write("#>\n\n")
            else:
                # pre-cond, if present
                if 'pre_condition' in T:
                    F.write("\"\"\"@ pre_condition:\n")
                    F.write(f"{T['pre_condition']}\n")
                    F.write("\"\"\"\n\n")

                    F.write("#< pre_condition_solution:\n")
                    F.write(f"{T['pre_condition_solution']}\n")
                    F.write("#>\n\n")

                #post-cond:
                F.write("\"\"\"@ post_condition:\n")
                F.write(f"{T['post_condition']}\n")
                F.write("\"\"\"\n\n")

                F.write("#< post_condition_solution:\n")
                F.write(f"{T['post_condition_solution']}\n")
                F.write("#>\n\n")

        with open(testPyFile, 'w') as F:
            F.write(f"# This is a generated file.\n\n")
            
            F.write("import itertools\n")
            F.write(f"import {tid}\n")
            F.write("\n")
            
            F.write(F"SUITE_TO_USE = \"{SUITE_TO_USE}\"\n")
            F.write("splitToken = \'===\'\n")
            F.write("NUMBER_OF_REPEATED_TEST = 1\n")
            F.write(F"WHAT_TO_TEST = \"{WHAT_TO_TEST}\"\n")
            F.write("ORIG_PROBLEMS = { }\n")
            F.write("\n")

            # pre-cond tests, if we have pre-cond:
            if 'pre_condition' in T:
                F.write("#< pre_condition_tests:\n")
                F.write(f"pre_condition_tests_{tid} = {T['pre_condition_tests']}\n")
                F.write("#>\n\n")

            # post-cond tests:
            F.write("#< post_condition_tests:\n")
            F.write(f"post_condition_tests_{tid} = {T['post_condition_tests']}\n")
            F.write("#>\n\n")

            # selectSuite:
            F.write("def selectSuite(rawTestcases):\n")
            F.write("   suites = [list(gr) for (key, gr) in itertools.groupby(rawTestcases, lambda e: e != splitToken) if key]\n")
            F.write("   if SUITE_TO_USE == \"base0\": return suites[0]\n")
            F.write("   if SUITE_TO_USE == \"base1\": return suites[0] + suites[1]\n")
            F.write("   if SUITE_TO_USE == \"validation\": return (suites[2])\n")
            F.write("   if SUITE_TO_USE == \"N0.3\":\n")
            F.write("        S = suites[0] \n")
            F.write("        k = max(1,int(int(len(S)/3))) \n")
            F.write("        return S[0:k] \n")
            F.write("   return sum(suites,[])\n")
            F.write("\n")

            # load_original_postcond
            F.write("import os\n")
            F.write("import json\n")
            F.write("\n")
            F.write("def load_original_postcond(Tid, loadedProblems):\n")
            F.write("   if len(loadedProblems) == 0 :\n")
            F.write("      filename = os.path.join(\"..\", \"..\", \"..\", \"..\", \"simple-specs.json\")\n")
            F.write("      with open(filename, \"r\") as fp:\n")
            F.write("         tasks = json.load(fp)\n")
            F.write("         for T in tasks:\n")
            F.write("            loadedProblems[T[\"task_id\"]] = T\n")
            F.write("   P = loadedProblems[Tid]\n")
            F.write("   origPostCond = P[\"post_condition_solution\"]\n")
            F.write("   k = origPostCond.find(\"(\")\n")
            F.write("   functionName = \"ORIG_post_solution_\" + Tid\n")
            F.write("   origPostCond2 = \"def \" + functionName + origPostCond[k:]\n")
            F.write("   return (functionName,origPostCond2)\n")
            F.write("\n")

            if WHAT_TO_TEST == "PROGRAM":
                # pre-cond, if present
                if 'pre_condition' in T:
                    F.write("\"\"\"@ pre_condition:\n")
                    F.write(f"{T['pre_condition']}\n")
                    F.write("\"\"\"\n\n")

                    F.write("#< pre_condition_solution:\n")
                    F.write(f"{T['pre_condition_solution']}\n")
                    F.write("#>\n\n")

                #post-cond:
                F.write("\"\"\"@ post_condition:\n")
                F.write(f"{T['post_condition']}\n")
                F.write("\"\"\"\n\n")

                F.write("#< post_condition_solution:\n")
                F.write(f"{T['post_condition_solution']}\n")
                F.write("#>\n\n")
            else:
                # solution-prg:
                F.write("#< program:\n")
                F.write(f"{T['program']}\n")
                F.write("#>\n\n")

            # test function:
            F.write(f"def test_{tid}():\n")
            F.write(f"    rawtestcases = post_condition_tests_{tid}\n")
            F.write("    suite = selectSuite(rawtestcases)\n")
            F.write("    if WHAT_TO_TEST == \"PROGRAM\" :\n")
            F.write("       for k in range(NUMBER_OF_REPEATED_TEST) :\n")
            F.write("          for tc in suite:\n")
            F.write("             prgInput = tc[1:]\n")
            if WHAT_TO_TEST == "PROGRAM":
                F.write(f"             retval = {tid}.Pr_{tid}(*prgInput)\n")
            else:
                F.write(f"             retval = Pr_{tid}(*prgInput)\n")

            F.write("             postCondInput = [retval] + prgInput\n")
            if WHAT_TO_TEST == "PROGRAM":
                F.write(f"             approved = check_post_solution_{tid}(*postCondInput)\n")
            else:
                F.write(f"             approved = {tid}.check_post_solution_{tid}(*postCondInput)\n")

            F.write(f"             if not approved: print(f\">>> Post-cond VIOLATION {tid}.\")\n")
            F.write("             assert approved\n")
            F.write("    else: # for testing the post-cond only \n")
            F.write(f"       Tid = \"{tid}\"\n")
            F.write("       global ORIG_PROBLEMS\n")
            F.write("       (postCondName2,origDef) = load_original_postcond(Tid,ORIG_PROBLEMS)\n")
            F.write("       try:\n")
            F.write("           exec(origDef,globals())\n")
            F.write("       except:\n")
            F.write("           print(\">>>>>> Ouch. The def of the solution post-cond CRASHED!\")\n")
            F.write("           print(origDef)\n")
            F.write("           return\n")
            F.write("       # now we run the tests, no need to do repeated tests here as the tests are fixed values\n")
            F.write("       for tc in suite:\n")
            F.write("          expectedValue = eval(f\"{postCondName2}(*{tc})\")  # Calculating regression oracle\n")
            if WHAT_TO_TEST == "PROGRAM":
                F.write(f"          approved = (check_post_solution_{tid}(*tc) == expectedValue)\n")
            else:
                F.write(f"          approved = ({tid}.check_post_solution_{tid}(*tc) == expectedValue)\n")

            F.write("          if not approved: print(f\">>> Post-cond of {Tid} has regression-violation on {tc}.\")\n")
            F.write("          assert approved\n")

        k += 1

    print(f">>> generated python-src for {k} problems")

import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("You have to specify the path to the json file and the folder where to place the generated files")
        exit(1)

    jsonFile = sys.argv[1]
    targetDir = sys.argv[2]

    if len(sys.argv) > 3:
        SUITE_TO_USE = sys.argv[3]
    if len(sys.argv) > 4:
        WHAT_TO_TEST = sys.argv[4]

    generatePythons(jsonFile,targetDir)
