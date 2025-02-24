from llama_cpp import Llama
from datetime import datetime
from typing import Dict
import time
import os

from openai4spi import PromptResponder, generate_results


class LLAMAcppClient(PromptResponder):
    """
    An instance of prompt-responder that uses a LLAMA cpp as backend model.
    """

    def __init__(self, client:Llama):
        PromptResponder.__init__(self)
        self.client = client

    def completeIt(self, multipleAnswer: int, prompt: str) -> list[str]:
        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        answers = []
        for k in range(multipleAnswer):

            # call the prompt
            A = self.client(prompt, temperature=0.7,max_tokens=1024 )

            # A = self.client.create_chat_completion(
            #     messages=[
            #         {"role": "system", "content": "You are an expert developer."},
            #         {
            #             "role": "user",
            #             "content": f"{prompt}"
            #         }
            #     ], temperature=0.7,max_tokens=1024
            # )

            answers.append(A["choices"][0]["text"].strip())

            # answers.append(A["choices"][0]['message']['content'].strip())

            if self.DEBUG:
                print(f">>> raw response {k}:\n {A}")
        return answers

if __name__ == '__main__':
    llamaClient = Llama(model_path="~/.local/share/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf", n_gpu_layers=-1)

    myAIclient = LLAMAcppClient(llamaClient)


    dataset = os.path.join( "../../llm4spiDatasets/data/HEx-compact.json")

    generate_results(myAIclient,
                     dataset,
                     specificProblem =  "HE0",
                     experimentName = "mistral-7b-instruct-v0.1.Q4_0",
                     enableEvaluation=True,
                     allowMultipleAnswers=10,
                     prompt_type="usePredDesc"
                     #prompt_type="cot2"
                     )