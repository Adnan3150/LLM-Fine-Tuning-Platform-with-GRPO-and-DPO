import torch
from transformers import BitsAndBytesConfig
from unsloth import FastLanguageModel
from config import MODEL_PATH
import os


def load_model():
    torch.cuda.empty_cache()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_PATH,
        max_seq_length=512,
        dtype=torch.float16,
        load_in_4bit=True,
        max_lora_rank=32,
        gpu_memory_utilization=0.9,
        fast_inference=True
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )  

    return model, tokenizer