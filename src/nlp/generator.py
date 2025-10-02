import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from .prompt import build_prompt
from .fewshots import FEWSHOTS

BASE_MODEL = "google/flan-t5-base"

class T2SQLGenerator:
    def __init__(self, schema_txt: str, fewshots: str = FEWSHOTS, model_name: str = BASE_MODEL):
        self.schema_txt = schema_txt
        self.fewshots = fewshots
        self.tok = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.eval()

    def generate(self, question: str, max_new_tokens: int = 128, num_beams: int = 4) -> str:
        prompt = build_prompt(self.schema_txt, question, self.fewshots)
        
        # Truncate input to fit within model's max length (512 tokens)
        # Reserve some tokens for generation
        max_input_length = 400
        ids = self.tok(prompt, return_tensors="pt", truncation=True, max_length=max_input_length).input_ids
        
        with torch.inference_mode():
            out = self.model.generate(ids, max_new_tokens=max_new_tokens, num_beams=num_beams)
        return self.tok.decode(out[0], skip_special_tokens=True).strip()