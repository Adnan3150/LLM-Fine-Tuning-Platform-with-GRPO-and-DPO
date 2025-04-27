# LLM-Fine-Tuning-Platform-with-GRPO-and-DPO
A web-based platform for fine-tuning LLMs using Reinforcement Learning from Human Feedback (RLHF). It features a user interface for prompt submission and feedback collection, and it employs GRPO and DPO algorithms for model training, with MongoDB for data storage.

Project Structure:
.
├── app/
│   ├── __init__.py          # App package initializer
│   ├── web.py               # Flask UI and endpoints for prompt input and feedback
│   ├── trainer.py           # Core training logic using GRPOTrainer
│   ├── model_loader.py      # Handles model loading, saving, and reloading
│   ├── state.py             # Manages shared state across threads and sessions
├── run.py                   # Entry point to launch web server and background trainer
├── config.py                # Config file for environment settings (HOST, PORT, etc.)

 Purpose:
This project is a human-in-the-loop reward trainer for fine-tuning LLMs using the GRPO (Generative Reward Policy Optimization) algorithm. It enables:
- Prompt submission via a web interface.
- Collection of multiple model completions.
- Rating and feedback from humans per completion.
- Fine-tuning of the model based on real-time feedback.
