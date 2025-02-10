# Use Google AI Studio API
# https://aistudio.google.com/
# Google provides free API access with rate limits
# https://aistudio.google.com/plan_information
# Google provides python API
# http://pypi.org/project/google-genai/

import os
import time

from google import genai
from google.genai import types

from openai4spi import PromptResponder, generate_results

class GoogleResponder(PromptResponder):
    """
    An instance of prompt-responder that uses Google models.
    Free Gemini models have 3 limits
    RPM: requests per minute
    TPM: tokens per minute
    RPD: requests per day
    """
    def __init__(self, client: genai.Client, modelId: str, rpm_limit: int, tpm_limit: int , rpd_limit: int):
        PromptResponder.__init__(self)
        self.client = client

        # to exceed num of request  per minute
        self.last_time_seen = -1
        # to set as parameters
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.rpd_limit = rpd_limit
        # used resources
        self.rpm_used = 0
        self.tpm_used = 0
        self.rpd_used = 0
        # timers for minutes and days
        self.minute_timer = 0
        self.day_timer = 0
        # save model name
        self.model_id = modelId


    def completeIt(self, multipleAnswer: int, prompt: str) -> list[str]:

        if self.DEBUG: print(">>> PROMPT:\n" + prompt)
        answers = []

        # Google client configuration
        cfg = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024
        )

        # first call
        if self.last_time_seen == -1:
            self.last_time_seen = time.time()
            passed_time = 0
        else:
            # time passed since the last call
            passed_time = time.time() - self.last_time_seen

        # More than one minute is passed
        if passed_time > 60:
            # reset minute counters
            self.minute_timer = 0
            self.rpd_used = 0
            self.tpm_used = 0

        # One day is passed
        if passed_time > 60 * 60 * 24:
            # reset day counters
            self.day_timer = 0
            self.rpd_used = 0

        # estimate token usage
        prompt_tokens = self.client.models.count_tokens(model=self.model_id, contents=prompt)


        # iterate
        for k in range(multipleAnswer):

            # check if free resource are consumed
            if self.rpm_used + 1 >= self.rpm_limit or self.tpm_used + prompt_tokens.total_tokens + 1 >= self.tpm_limit :
                sleep_time = max(1,60 - self.minute_timer)
                if self.DEBUG: print(f">>> sleep {sleep_time}s\n" )
                time.sleep(sleep_time)
                self.rpm_used = 0
                self.tpm_used = 0
                self.minute_timer = 0

            # rpd finished
            if self.rpd_used >= self.rpd_limit :
                sleep_time = max(1, ( 60 * 60 * 12) - self.day_timer)
                if self.DEBUG: print(f">>> sleep {sleep_time}s\n")
                time.sleep(sleep_time)
                self.rpd_used = 0
                self.day_timer = 0

            t0 = time.time()
            response = self.client.models.generate_content( model = self.model_id, contents = prompt, config = cfg )
            used_time = time.time() - t0
            self.minute_timer += used_time
            self.day_timer += used_time
            self.rpm_used += 1
            self.rpd_used += 1
            self.tpm_used += response.usage_metadata.total_token_count

            usage_data = response.usage_metadata
            answers.append(response.text)

        self.last_time_seen = time.time()
        return answers


if __name__ == '__main__':
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    googleClient = genai.Client(api_key=gemini_api_key)

    """
    An instance of prompt-responder that uses an LLM available at Google AI Studio as the backend model.
    """

    modelId = "gemini-2.0-flash"

    myAiClient = GoogleResponder(googleClient, modelId, 10, 1000000, 1000)

    ROOT = os.path.dirname(os.path.abspath(__file__))
    dataset = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data", "HEx-compact.json")

    generate_results(myAiClient,
                     dataset, "HE1",
                     experimentName="testing_google_api",
                     enableEvaluation=True,
                     allowMultipleAnswers=12,
                     prompt_type="usePrgDesc"
                     )

