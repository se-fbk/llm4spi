#
# Example code to evalute open-source LLMs provided by Groq.com on its ability to produce 
# pre-/post-conditions.
# See e.g. https://console.groq.com/docs/overview
# 
# The example is in the main-function.
#
from datetime import datetime
from typing import Dict, List
from openai import OpenAI
import os
import time

from openai4spi import PromptResponder, generate_results

#
# Groq actually has its own client-side API, but we will use OpenAI API since this is
# also supported.
#
class MyGroqClient(PromptResponder):
    """
    An instance of prompt-responder that uses an LLM available at Groq as the backend model.
    """
    def __init__(self,client: OpenAI, modelId:str):
        """
        Expecting an OpenAI-client.
        """
        PromptResponder.__init__(self)
        self.client = client
        self.model = modelId
        # to keep track of time, towards deciding to pause so as not
        # to exceed num of tokens/minute 
        self.t0 = None
        self.maxNumOfTokensPerMiniteLIMIT = 6000 # pfff :(
    
    def completeIt(self, multipleAnswer:int, prompt:str) -> list[str] :
        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        #
        # Groq-side does not currently support multiple answers; so we will explicitly ask one at a time.
        #
        responses = []
        if self.t0 == None:
            self.t0 = time.time()
        totTokensSinceLastPause = 0
        for k in range(multipleAnswer):
            completion = self.client.chat.completions.create(
                model = self.model,
                temperature=0.7,
                max_tokens=1024,
                # n = ... ,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                    ]
                )
            R = completion.choices[0].message.content
            estimatedNumOfTokens = 3* len(R.split())
            responses.append(R)
            if self.DEBUG: 
                print(f">>> raw response {k} (estimated #tokens {estimatedNumOfTokens}):\n {R}")
            totTokensSinceLastPause = totTokensSinceLastPause + estimatedNumOfTokens
            timeSinceLastPause = time.time() - self.t0
            if multipleAnswer>1 and timeSinceLastPause >= 0.8*60 or totTokensSinceLastPause >= 0.8 * self.maxNumOfTokensPerMiniteLIMIT:
                # add pause untill one minute over:
                sleepTime = max(5,60 - timeSinceLastPause)
                if self.DEBUG: 
                    print(f">>> SLEEPING {sleepTime}s ...")
                self.t0 = time.time()
                time.sleep

        return responses
    
if __name__ == '__main__':
    groq_api_key = os.environ.get('GROQ_API_KEY') 
    openAIclient = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key)
    
    # modelId = "gemma2-9b-it"
    #modelId = "llama3-70b-8192"
    modelId = "deepseek-r1-distill-llama-70b"
    
    myAIclient = MyGroqClient(openAIclient,modelId)
    myAIclient.DEBUG = True

    ROOT = os.path.dirname(os.path.abspath(__file__))
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "mini.json")
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")

    generate_results(myAIclient,
                     dataset, "HE1",
                     experimentName = "HE1-deepseek-r1-distill-llama-70b",     
                     enableEvaluation=True, 
                     allowMultipleAnswers=10,
                     prompt_type="usePrgDesc"
                     #prompt_type="cot2"
                     )
    