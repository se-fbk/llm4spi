#
# Example code to evalute GPT4All LLMs on its ability to produce pre-/post-conditions.
#
from datetime import datetime
from gpt4all import GPT4All
from typing import Dict
import time
import os

from data import ZEROSHOT_DATA
from openai4spi import PromptResponder, generate_results

class MyGPT4ALL_Client(PromptResponder):
    """
    An instance of prompt-responder that uses a GPT4All's LLM as the backend model.
    """
    def __init__(self, client:GPT4All):
        PromptResponder.__init__(self)
        self.client = client
    
    def completeIt(self, multipleAnswer:int, prompt:str) -> list[str]:
        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        with self.client.chat_session():
            answers = []
            for k in range(multipleAnswer):
                A = self.client.generate(prompt, 
                                temp=0.7,
                                max_tokens=1024,
                                repeat_penalty=1.0,
                                repeat_last_n=multipleAnswer
                                )
                answers.append(A)
                #answer2 = self.client.generate("Please only give the Python code, without comment.", max_tokens=1024)
                # srtipping header seems difficult for some LLM :|
                #answer3 = self.client.generate("Please remove the function header.", max_tokens=1024)
        
        if self.DEBUG: 
            for k in range(len(answers)):
                print(f">>> raw response {k}:\n {answers[k]}")
        return answers


if __name__ == '__main__':
    #gpt4allClient = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", model_path="/root/models", device="cuda:NVIDIA A16 (3)") #device is specific to cluster's GPU, change accordingly when run on a different computer
    #gpt4allClient = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", model_path="../../models", device="cpu")
    #gpt4allClient = GPT4All("mistral-7b-openorca.Q4_0.gguf", model_path="../../models", device="cpu")
    # this star-coder gives load-error
    #gpt4allClient = GPT4All("starcoder-q4_0.gguf", model_path="../../models", device="cpu")
    gpt4allClient = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="../../models", device="cpu")
    
    
    myAIclient = MyGPT4ALL_Client(gpt4allClient)

    dataset = ZEROSHOT_DATA
    ROOT = os.path.dirname(os.path.abspath(__file__))
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "x.json")
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")

    generate_results(myAIclient,
                     dataset, 
                     specificProblem =  "arith_4",
                     experimentName = "orca-mini",     
                     enableEvaluation=True, 
                     allowMultipleAnswers=4,
                     prompt_type="usePredDesc"
                     #prompt_type="cot2"
                     )