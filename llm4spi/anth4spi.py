from datetime import datetime
from typing import Dict, List
from anthropic import Anthropic
import anthropic
import os
import time

from openai4spi import PromptResponder, generate_results



class MyAnthorpicClient(PromptResponder):
    """
    An instance of prompt-responder that uses an LLM available at Groq as the backend model.
    """
    def __init__(self, client:Anthropic, modelId:str):
        """
        Expecting an Anthropic client.
        """
        PromptResponder.__init__(self)
        self.client = client
        self.model = modelId
        self.sleepTime = None
    
    def completeIt(self, multipleAnswer:int, prompt:str) -> list[str]:
        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        answers = []
        for k in range(multipleAnswer):
            msg = self.client.messages.create(
                max_tokens=1024,
                temperature=0.7,
                messages=[ {"role": "user", "content": prompt }],
                model = self.model
            )
            A = msg.content[0].text
            answers.append(A)
            if self.DEBUG: 
                print(f">>> raw response {k}:\n {A}")
        if self.sleepTime != None and self.sleepTime > 0 :
            if self.DEBUG: 
                print(f">>> SLEEPING {self.sleepTime}s ...")
            time.sleep(self.sleepTime)
        return answers
    

if __name__ == '__main__':
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY') 
    underlying_client = Anthropic(api_key = anthropic_api_key)

    # modelId = "claude-3-5-sonnet-latest"
    modelId = "claude-3-haiku-20240307"  #cheapest
    
    myAIclient = MyAnthorpicClient(underlying_client,modelId)
    myAIclient.DEBUG = True
    myAIclient.sleepTime = 20

    ROOT = os.path.dirname(os.path.abspath(__file__))
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "mini.json")
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")

    generate_results(myAIclient,
                     dataset, 
                     specificProblem = None,
                     experimentName = "claude-3",     
                     enableEvaluation=True, 
                     allowMultipleAnswers=10,
                     prompt_type="usePrgDesc"
                     #prompt_type="cot2"
                     )