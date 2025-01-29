#
# Example code to evalute open-source LLMs provided by Hugging Face on its ability to produce 
# pre-/post-conditions.
# 
# See: https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client
#
# The example is in the main-function.
#
from huggingface_hub import InferenceClient

from typing import Dict, List
import os


from openai4spi import PromptResponder, MyOpenAIClient, generate_results
from prompting import create_prompt


class MyHugginface_Client(PromptResponder):
    """
    An instance of prompt-responder that uses a Hugging Face LLM as the backend model.
    """
    def __init__(self, client:InferenceClient, modelId:str):
        PromptResponder.__init__(self)
        self.client = client
        self.model = modelId 

    def completeIt(self, multipleAnswer:int, prompt:str) -> list[str]:
        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        responses = []
        # Hugging Face does not support returning multiple answers for
        # the same prompt; or ... it could be depending on the model. For now
        # We will just iterate over it, repeating the query n-times:
        for k in range(multipleAnswer):
            # iterating inside the session does not work for various (open source) LLMs,
            # they keep giving the same answer despite the repeat-penalty
            completion = self.client.chat.completions.create(
                model = self.model,
                temperature=0.7,
                max_tokens=1024,
                # n = ... ,  --> Not supported by HF :(
                 messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                    ]
            )
            R = completion.choices[0].message.content
            responses.append(R)

        return responses
    

if __name__ == '__main__':
    Huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY') 
    #client = InferenceClient(provider="together", api_key=Huggingface_api_key)
    client = InferenceClient(api_key=Huggingface_api_key)
    model = "google/gemma-2-27b-it"

    # well these models are there, but too big. They won't load:
    #model = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
    #model = "deepseek-ai/DeepSeek-R1"
    #model = "deepseek-ai/DeepSeek-V2"

    myAIclient = MyHugginface_Client(client, model)
    myAIclient.DEBUG = True

    ROOT = os.path.dirname(os.path.abspath(__file__))
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")
    #dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")

    generate_results(myAIclient,
                     dataset, 
                     specificProblem = "HE0" ,
                     experimentName = "coba-hf",     
                     enableEvaluation = True, 
                     allowMultipleAnswers = 3,
                     prompt_type = "usePrgDesc"
                     #prompt_type="cot2"
                     )
    
    
