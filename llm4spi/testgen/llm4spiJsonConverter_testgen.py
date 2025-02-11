#
# For converting problems that are originally formulated in the llm4spi json format
# to individual Pyhton-script per problem.
#
import os
import json

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

            # solution-prg:
            F.write("#< program:\n")
            F.write(f"{T['program']}\n")
            F.write("#>\n\n")

        k += 1

    print(f">>> generated python-src for {k} problems")

import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("You have to specify the path to the json file and the folder where to place the generated files")
        exit(1)

    jsonFile = sys.argv[1]
    targetDir = sys.argv[2]
    generatePythons(jsonFile,targetDir)
