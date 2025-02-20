#
# A simple command-line runner for llm4spi
#
import sys, getopt
import os
import time
from openai4spi import PromptResponder, generate_results, MyOpenAIClient
from llm4spi import MyGPT4ALL_Client
from groq4spi import MyGroqClient
from openai import OpenAI
from gpt4all import GPT4All
from google import genai
from google4spi import GoogleResponder

DEBUG = True


# available command-line options:
providers = ["openAI", "openAI-1x","gpt4all", "groq", "gemini"]
# openAI --> single query get multiple answer enabled
# openAI-1x --> multiple answers are queried separately one at a time
options = [
   ("provider",  "The name of the LLM provider, e.g. openAI. Mandatory."),
   ("model",     "The name of the LLM to use, e.g. gpt3.5. Mandatory."),
   ("benchmarkDir", "The folder where the benchmark is located. If not specified: ../../llm4spiDatasets/data"),
   ("benchmark", "The name of the benchmark-file to target, e.g. simplespecs.json. Mandatory."),
   ("prompt_type", "Specify the type of prompt to use. If not present, then usePrgDesc is used."),
   ("specificProblem", "If present specifies a single problem to test."),
   ("experimentName",  "The name of the experiment. Reports will be produced prefixed with this name."),
   ("enableEvaluation", "If present will enable or disable evaluation. If not present, evaluation is enabled."),
   ("allowMultipleAnswers", "If present specifies how many answers per problem are requested. If not present it is 1."),
   ("gpt4all_localModelPath", "If a local GPT4ALL model is used, this point to the folder where GPT4AALL models are placed. Default is ../../models"),
   ("gpt4all_device", "If a local GPT4ALL model is used, this specifies to use cpu or gpu-id for running the model. if not specified, cpu is used."),
   ("gemini_rpm", "Request per minute for Google Gemini models."),
   ("gemini_tpm", "Tokens per minute for Google Gemini models."),
   ("gemini_rpd", "Request per day for Google Gemini models.")
]

helptxt = "python clispi.py [--option=arg]*\n"
helptxt += "   Options:\n"
for o in options:
   helptxt +=  f"   --{o[0]} : {o[1]}\n" 

def main(argv):
   ROOT = os.path.dirname(os.path.abspath(__file__))
   provider_ = None
   model_ = None
   benchmarkDir_ = os.path.join(ROOT, "..", "..", "llm4spiDatasets", "data")
   benchmark_ = None
   experimentName_ = None
   prompt_type_ = "usePrgDesc"
   specificProblem_ = None
   enableEvaluation_ = True
   allowMultipleAnswers_ = 1
   gpt4all_localModelPath_ = os.path.join(ROOT, "..", "..", "models") 
   gpt4all_device_ = "cpu"
   gemini_rpm_ = 15
   gemini_tpm_ = 1000000
   gemini_rpd_ = 1500
   try:
      opts, args = getopt.getopt(argv,"h", [ o[0] + "=" for o in options])
   except getopt.GetoptError:
      print (helptxt)
      sys.exit(2)
   for opt, arg in opts:
      match opt:
         case "-h":
            print (helptxt)
            sys.exit()
         case "--provider" :
            provider_ = arg
            if not (provider_ in providers) :
               print (f">> Unknown provider: {provider_}")
               sys.exit(2)
         
         case "--model" : model_ = arg
         case "--prompt_type" : prompt_type_ = arg
         case "--gpt4all_localModelPath" : gpt4all_localModelPath_ = arg
         case "--gpt4all_device" : gpt4all_device_ = arg

         case "--benchmark" : benchmark_ = arg
         case "--benchmarkDir" : benchmarkDir_ = arg
         case "--specificProblem" : specificProblem_ = arg
         case "--enableEvaluation" : enableEvaluation_ = bool(arg)
         case "--allowMultipleAnswers" : allowMultipleAnswers_ = int(arg)
         case "--experimentName" : experimentName_ = arg

         case "--gemini_rpm": gemini_rpm_ = int(arg)
         case "--gemini_tpm": gemini_tpm_ = int(arg)
         case "--gemini_rpd": gemini_rpd_ = int(arg)

   # create the client:
   match provider_ :
      case "openAI" : 
          openai_api_key = os.environ.get('OPENAI_API_KEY') 
          openAIclient = OpenAI(api_key=openai_api_key)
          myAIclient = MyOpenAIClient(openAIclient,model_)
      case "openAI-1x" : 
          openai_api_key = os.environ.get('OPENAI_API_KEY') 
          openAIclient = OpenAI(api_key=openai_api_key)
          myAIclient = MyOpenAIClient(openAIclient,model_)
          myAIclient.enableMultipleAnswer = False
      case "gpt4all" :
          gpt4allClient = GPT4All(model_, model_path=gpt4all_localModelPath_, device=gpt4all_device_)
          myAIclient = MyGPT4ALL_Client(gpt4allClient)
      case "groq" :
          groq_api_key = os.environ.get('GROQ_API_KEY') 
          openAIclient = OpenAI(base_url="https://api.groq.com/openai/v1",
                                api_key=groq_api_key)    
          myAIclient = MyGroqClient(openAIclient,model_)
      case "gemini" :
          gemini_api_key = os.environ.get('GEMINI_API_KEY')
          geminiClient = genai.Client(api_key=gemini_api_key)
          myAIclient = GoogleResponder(client=geminiClient, modelId=model_, rpm_limit=gemini_rpm_, tpm_limit=gemini_tpm_, rpd_limit=gemini_rpd_)


   myAIclient.DEBUG = DEBUG

   # run the analysis:
   dataset = os.path.join(benchmarkDir_, benchmark_)
   if experimentName_ == None:
      experimentName_ = f"{model_}_{prompt_type_}"
   generate_results(myAIclient,
                    dataset, 
                    specificProblem  = specificProblem_ ,
                    experimentName   = experimentName_,     
                    enableEvaluation = enableEvaluation_, 
                    allowMultipleAnswers = allowMultipleAnswers_,
                    prompt_type = prompt_type_
                    )
   
   
if __name__ == "__main__":
   main(sys.argv[1:])
