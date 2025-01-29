import vertexai
import openai

# from google.auth import default, transport

# from datetime import datetime
# from typing import Dict, List
# import time

# from data import ZEROSHOT_DATA, read_problems, write_jsonl
# from openai4spi import PromptResponder, generate_results
# from prompting import create_prompt
# from evaluation import evaluate_task_results

# TODO(developer): Update and un-comment below line
# PROJECT_ID = "your-project-id"
# location = "us-central1"
# PROJECT_ID = "openai-llm-meta"
# vertexai.init(project=PROJECT_ID, location=location)

# # Programmatically get an access token
# credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
# auth_request = transport.requests.Request()
# credentials.refresh(auth_request)

# # # OpenAI Client
# client = openai.OpenAI(
#     base_url=f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{location}/endpoints/openapi",
#     api_key=credentials.token,
# )

# response = client.chat.completions.create(
#     model="google/gemini-1.5-flash-002",
#     messages=[{"role": "user", "content": "Why is the sky blue?"}],
# )

# print(response.choices[0].message.content)
import openai

import os
from google.auth import default, transport
from datetime import datetime
from typing import Dict, List
import time

from data import ZEROSHOT_DATA, read_problems, write_jsonl
from openai4spi import PromptResponder, generate_results
from prompting import create_prompt
from evaluation import evaluate_task_results



class MyVertexAIClient(PromptResponder):
    """
    An instance of PromptResponder that uses Google Vertex AI's models as the backend.
    """
    def __init__(self, client: openai.OpenAI, modelID: str):
        PromptResponder.__init__(self)
        
        self.client = client
        self.model = modelID



    def completeIt(self, prompt: str) -> str:
        if self.DEBUG: 
            print(">>> PROMPT:\n" + prompt)

        retries = 6  # Number of retries
        delay = 2  # Initial delay (in seconds) for the first retry attempt 


        for attempt in range(retries):
            try:
                # Make the API request
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = completion.choices[0].message.content
                
                if self.DEBUG:
                    print(">>> Raw response:\n" + response)
                return response
            except openai.RateLimitError as e:
                # Handle rate limit error by retrying after a delay
                print(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)  # Wait for a specific time before retrying
                delay *= 2  # Exponential backoff (increase delay after each retry)
            except Exception as e:
                # Handle other types of exceptions
                print(f"An error occurred: {e}")
                break  # Stop retrying if a different error occurs
        return "Error: Could not complete request after retries."

if __name__ == '__main__':
    # Configuration
    project_id = "openai-llm-meta"
    location = "us-central1"
    model_name = "google/gemini-1.5-pro-002"  # Replace with desired model
    # model_name = "code-bison@002" 
    vertexai.init(project=project_id, location=location)

    # Programmatically get an access token
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_request = transport.requests.Request()
    credentials.refresh(auth_request)
    
    googleclient = openai.OpenAI(
    base_url=f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/endpoints/openapi",
    api_key=credentials.token,
    )
    
    myAIclient = MyVertexAIClient(googleclient, model_name)
    myAIclient.DEBUG = True

    # Dataset configuration
    dataset = ZEROSHOT_DATA
    ROOT = os.path.dirname(os.path.abspath(__file__))
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "simple-specs.json")
    # modelIds = ["google/gemini-2.0-flash-exp", "google/gemini-1.5-flash-002", "google/gemini-1.5-pro-002"]
    modelIds = ["google/gemini-1.5-pro-002"]
    prompt_types = ["usePrgDesc", "usePrgDesc_0", "cot1", "cot1_0", "usePredDesc", "usePredDesc_0", "xcot1", "xcot1_0"]
    for modelId in modelIds:
        myAIclient.model = modelId  # Set model ID
        sanitized_modelId = modelId.replace("/", "-")  # Replace '/' with '-'
        for prompt_type in prompt_types:
            experiment_name = f"{sanitized_modelId}-{prompt_type}" 
            generate_results(myAIclient,
                             dataset, 
                             specificProblem = None,
                             experimentName = experiment_name,     
                             enableEvaluation=True, 
                             prompt_type=prompt_type
                             )

# Example response:
# The sky is blue due to a phenomenon called **Rayleigh scattering**.
# Sunlight is made up of all the colors of the rainbow.
# As sunlight enters the Earth's atmosphere ...