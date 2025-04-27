import threading
import os
import time
from datasets import Dataset
from trl import GRPOConfig, GRPOTrainer
from app.state import prompt_queue, session_store, state_lock
from config import LORA_PATH
from app.model_loader import load_model
import torch
from functools import wraps

# Load model and tokenizer
model, tokenizer = load_model()
device = next(model.parameters()).device
print(f"[INFO] Model device: {device}")



# Wait for human rating
# Wait for human rating
def wait_for_rating(session_id):
    session = session_store[session_id]
    print("waiting for ratings to be entered")
    session["event"].wait(timeout=1800)
    session["completions"]=[]
    print("ratings",session["ratings"])
    return session["ratings"]
    
    
# Reward function
def rf(prompts: list, completions: list, **kwargs) -> list:
    print("completions",completions)
    session_id = kwargs.get("session_id")
    session = session_store.get(session_id, {})
    # Set or update fields without removing existing ones
    session["prompt"] = prompts[0]
    session["completions"] = completions
    session["ratings"] = [None] * len(completions)
    print("rating set to NOne")
    # Only set event if not already set
    session["event"] = threading.Event()

    # Ensure num_of_epochs is preserved
    session.setdefault("num_of_epochs", 0)

    # Save updated session
    session_store[session_id] = session

    print(f"[INFO] Awaiting ratings at: /rate/{session_id}")
    return wait_for_rating(session_id)


# GRPO Config
training_args = GRPOConfig(
    learning_rate=5e-3,
    weight_decay=0.1,
    warmup_ratio=0.1,  
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",
    logging_steps=1,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_generations=4,
    max_prompt_length=128,
    max_completion_length=128,
    max_steps=2,
    save_steps=1,
    max_grad_norm=0.1,
    report_to="none",
    output_dir="deepseek-grpo-output",
    per_gpu_eval_batch_size=1,
)

# Trainer
trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[rf],
    args=training_args,
    train_dataset=[],
)

# Reload LoRA weights if available
def reload_model():
    if os.path.exists(LORA_PATH):
        model.load_lora(LORA_PATH)
        print("[INFO] Loaded previous LoRA weights.")
    trainer.model = model
    
def make_reward_func(session_id):
    def reward_func(**kw):
        return rf(kw["prompts"], kw["completions"], session_id=session_id)
    return reward_func
    
# Background training loop
def start_background_training():
    while True:
        with state_lock:
            if prompt_queue:
                current = prompt_queue.pop(0)
                session_id = current["session_id"]
                prompt = current["prompt"]
                print("prompt",prompt)
                try:
                    dataset = Dataset.from_list([{"prompt": prompt}])               
                    trainer.train_dataset = dataset
                    trainer.reward_funcs = [make_reward_func(session_id)]
                    trainer.train()
                    model.save_pretrained(LORA_PATH)
                    reload_model()
                except Exception as e:
                    print(f"[ERROR] Training failed for session {session_id}: {e}")
                finally:
                    # ? CLEANUP: session data after training and rating
                    session_store.pop(session_id, None)
        time.sleep(5)

