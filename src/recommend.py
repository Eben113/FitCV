from resume import CVParse
from github import relevance_filter
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct")
model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct")

device = "cuda" if torch.cuda.is_available() else "cpu"
gen_pipeline = pipeline(task="text-generation", model=model, tokenizer = tokenizer)

def recommend(CV, Repo_link):
    skills = CVParse.extract("skills")