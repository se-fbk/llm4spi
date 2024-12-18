# Project: using LLMs to write SPises

Since LLMs are so smart, we wonder how good they are for generating 'formal' specifications. Or at least, specifications that can be executed so we can actually use them for checking the inputs and outputs of programs under test.

The project provides a framework for assessing LLMs ability to extract formal pre- and post-conditions from a program's description. We can consider both commercial LLMs like OpenAI GPTs as well open source LLMs.

Example prompt-1: _Give a Python program `Postcondition(x,y,z)` that checks whether the sum of x and y is zero or equal to z_

Answer by Orca-mini-3B: 😅

```python
Postcondition(x,y,z):
     if x + y == 0 or x - y == 0 or z - x == 0:
     return True
     else:
     return False
```

Example prompt-2: _Give a Python program `Postcondition(joke:str)` that checks whether the joke is funny._ 😉

Answer by OpenAI's GPT:

```python
def Postcondition(joke: str) -> bool:
    # Use VADER for a basic sentiment analysis approach
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(joke)

    # Consider a joke "funny" if it has a positive sentiment
    if sentiment['pos'] > sentiment['neg']:
        return True
    return False

# Example usage
joke = "Why don't scientists trust atoms? Because they make up everything!"
print(Postcondition(joke))  # Output: True
```



  |  | simple-specs-40 | HEx-26 |
  |--|----------|----|
  | GPT 4o          | 92.5%  |
  | GPT 4 turbo          | 87.5%  |
  | GPT 3.5 turbo        | 85%  | 57% (base-test1) / 73% |
  | codellama-7b-instruct.Q8_0           | 27.5% (using prg-desc) / 35%  | 15% |
  | codellama-13b-instruct.Q6_K          | 32.5%, but slow  |
  | codellama-13b-instruct.Q4_0 | 30% |
  | Meta-Llama-3-8B-Instruct.Q4_0 | 35% (using prg-desc) / 35%  |
  | Llama-3-15b-Instruct-GLUED.Q6_K | 32.5%, but very slow |
  | Meta-Llama-3-8B-Instruct (Groq, possibly 16f) |  | 48% using prg-desc |
  | Meta-Llama-3-70B-Instruct (Groq, possibly 16f) |  | 65.5% using prg-desc |
  | mistral-7b-instruct-v0.2.Q8_0      | 27.5%  |
  | orca-2-13b.Q4_0   | 15%  |
  | wizardcoder-python-13b-v1.0.Q4_K_M | 10%, very slow |
  | gemma2-9b-it (Groq, possibly 16f) | 48% using prg-desc |




#### Using GPT4All.

You can use a [Docker-image with GPT4All installed](https://hub.docker.com/r/morgaine/llm4spi). The image has:

* Ubuntu 22-04
* Python 3.12 installed
* NVIDIA Container Toolkit installed
* Vulkan SDK installed
* GPT4All installed (as a Python package)
