import requests
from datasets import load_dataset, Dataset
import base64
token = "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"
headers = {"Authorization": f"token ghp_{token}"}

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
    user_prompt2 = "From the contents of this file list five to ten skills that were used in this project and can be added to the skills section of your resume, use one or two words per skill and in comma-separated form"
    assistant_prompt = "Skills I have that I demonstrated here were Python programming,   "
  return user_prompt1, user_prompt2, assistant_prompt

def repo_walk(df, role, tokenizer, gen_pipeline):
  def prompt(file_type, role, url, main=False):
    user1, user2, assistant4des = return_template(file_type, role, main, purpose="describe")
    doc = requests.get(url, headers=headers).json()
    doc = base64.b64decode(doc["content"])
    description_prompt = tokenizer.apply_chat_template([{"role":"system", "content":"You are a "+ role +" applying for a job role"},
                                            {"role":"user", "content":user1+ doc.decode("utf-8")+ user2},
                                            {"role":"assistant", "content":assistant4des}], tokenize=False, continue_final_message=True)
    print(len(tokenizer(description_prompt)['input_ids']))
    user1, user2, assistant4ski = return_template(file_type, role, main, purpose="skills")
    skills_prompt = tokenizer.apply_chat_template([{"role":"system", "content":"You are a "+ role +" applying for a job role"},
                                            {"role":"user", "content":user1+ doc.decode("utf-8")+ user2},
                                            {"role":"assistant", "content":assistant4ski}], tokenize=False, continue_final_message=True)

    return description_prompt, skills_prompt, assistant4des, assistant4ski

  def func(record):
    if record["directory"] == record["repo"] + "/" + "readme":
      prompt1, prompt2, cut1, cut2 = prompt("README", role, record["url"],  main=True)
    elif record["directory"].split("/")[-1] == "readme":
      prompt1, prompt2, cut1, cut2 = prompt("README", role, record["url"],  main=False)
    else:
      prompt1, prompt2, cut1, cut2 = prompt("code", role, record["url"],  main=False)
    return record["repo"], prompt1, prompt2, cut1, cut2

  def truncate(prompt_rec):
    des_index = prompt_rec["description"].find(prompt_rec["cut1"]) + len(prompt_rec["cut1"]) - 1
    ski_index = prompt_rec["skills"].find(prompt_rec["cut2"]) + len(prompt_rec["cut2"]) - 1
    return {'description': prompt_rec["description"][des_index:], 'skills':prompt_rec["skills"][ski_index:]}

  prompts = df.apply(func, axis=1, result_type="expand")
  prompts.columns = ("repo",  "prompt1", "prompt2", "cut1", "cut2")
  prompts = Dataset.from_pandas(prompts)
  descriptions = gen_pipeline(prompts["prompt1"], max_new_tokens=100)
  skills = gen_pipeline(prompts["prompt2"], max_new_tokens=50)
  res = Dataset.from_dict({"repo": prompts["repo"], "description":descriptions, "skills":skills, "cut1":prompts["cut1"], "cut2":prompts["cut2"]})
  res = res.map(lambda x: {'description': x['description'][0]['generated_text'],
                     'skills': x['skills'][0]['generated_text']})
  res = res.map(truncate)
  return res