import base64
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM
from datasets import load_dataset
import torch

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct")

model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct")

firstJs

tokens = tokenizer.apply_chat_template([{"role":"system", "content":"You are a python developer applying for a job role"},
                                        {"role":"user", "content":"These are the contents of one of your code files: "+tkns.decode("utf-8")+ "list out ten skills without explanation that this are demonstrated in this code and would be relevant to the job and can be added to the skills section of your resume"},
                                        {"role":"assistant", "content":"ten skills demonstrated here are: 1. Python 2."}], tokenize=False, continue_final_message=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
gen_pipeline = pipeline(task="text-generation", model=model, tokenizer = tokenizer)

def return_template(file_type, role, main=False, purpose="describe"):
  if file_type == "code":
    user_prompt1 = "These are the contents of one of the code files from one of your github repos"
  elif file_type == "README" and main == True:
    user_prompt1 = "These are the contents of the main README file from one of your github repos"
  else:
    user_prompt1 = "These are the contents of one of the readme files from one of your github repos"

  if purpose == "describe" and main == True:
    user_prompt2 = "Write a one paragraph description of the project for the projects part of your resume"
    assistant_prompt = "During this project I "
  elif purpose == "describe":
    user_prompt2 = "Write a one line description of what this part of the project does"
    assistant_prompt = "This part of the project is where I "
  else:
    user_prompt2 = "From the contents of this file list five to ten skills that were used in this project and can be added to the skills section of your resume"
    assistant_prompt = "Skills I have that I demonstrated here were Python programming,   "
  return user_prompt1, user_prompt2, assistant_prompt

def repo_walk(df, role):
  def prompt(file_type, role, url, main=False):
    user1, user2, assistant4des = return_template(file_type, role, main, purpose="describe")
    doc = requests.get(url, headers=headers).json()
    #print(doc)
    doc = base64.b64decode(doc["content"])
    description_prompt = tokenizer.apply_chat_template([{"role":"system", "content":"You are a "+ role +" applying for a job role"},
                                            {"role":"user", "content":user1+ doc.decode("utf-8")+ user2},
                                            {"role":"assistant", "content":assistant4des}], tokenize=False, continue_final_message=True)
    """description = gen_pipeline(tokens, max_new_tokens=150)[0]["generated_text"]

    index = description.find(assistant) + len(assistant) - 1
    description = description[index:]"""

    user1, user2, assistant4ski = return_template(file_type, role, main, purpose="skills")
    skills_prompt = tokenizer.apply_chat_template([{"role":"system", "content":"You are a "+ role +" applying for a job role"},
                                            {"role":"user", "content":user1+ doc.decode("utf-8")+ user2},
                                            {"role":"assistant", "content":assistant4ski}], tokenize=False, continue_final_message=True)

    """skills = gen_pipeline(tokens, max_new_tokens=150)[0]["generated_text"]

    index = skills.find(assistant) + len(assistant) - 1
    skills = skills[index:]"""

    return description_prompt, skills_prompt, assistant4des, assistant4ski

  def func(record):
    if record["directory"] == record["repo"] + "/" + "readme":
      prompt1, prompt2, cut1, cut2 = prompt("README", role, record["url"],  main=True)
    elif record["directory"].split("/")[-1] == "readme":
      prompt1, prompt2, cut1, cut2 = prompt("README", role, record["url"],  main=False)
    else:
      prompt1, prompt2, cut1, cut2 = prompt("code", role, record["url"],  main=False)
    return prompt1, prompt2, cut1, cut2

  def truncate(prompt_rec):
    des_index = prompt_rec["description"].find(prompt_rec["cut1"]) + prompt_rec["cut1"] - 1
    ski_index = prompt_rec["skills"].find(prompt_rec["cut2"]) + prompt_rec["cut2"] - 1
    return prompt_rec["description"][des_index:], prompt_rec["skills"][ski_index:]

  prompts = df.apply(func, axis=1, result_type="expand")
  descriptions = gen_pipeline(prompts[0], max_new_tokens=50)
  skills = gen_pipeline(prompts[1], max_new_tokens=50)
  res = pd.DataFrame({"description":descriptions, "skill":skills, "cut1":prompts[2], "cut2":prompts[3]})
  prompts_truncated = df.apply(truncate, axis=1, result_type="expand")
  df["description"] = prompts_truncated[0]
  df["skills"] = prompts_truncated[1]


  """describeDict = {}
  skillsList = []
  if list(linkDict.keys())[0] == "readme":
    description, skills = prompt("README", role, linkDict["readme"], main=True)
    describeDict["main_readme"] = description
    skillsList.append(skills)
  linkDict.pop("readme")
  def walk(linkDict):
    i = 1
    for k,v in linkDict.items():
      if type(v) == dict:
        walk(v)
      elif k == "readme":
        description, skills = prompt("README", role, v, main=False)
        describeDict["readme "+ str(i)] = description
        i += 1
        skillsList.append(skills)
      else:
        description, skills = prompt("README", role, v, main=False)
        skillsList.append(skills)
  walk(linkDict)
  return describeDict, skillsList"""
