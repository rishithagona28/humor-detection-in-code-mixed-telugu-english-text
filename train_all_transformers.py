import os
import gc
import json
import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer
)

# Optional: Mount Google Drive if running in Colab
try:
    from google.colab import drive
    drive.mount('/content/drive')
    DRIVE_MOUNTED = True
    print("✅ Google Drive mounted successfully!")
except ImportError:
    DRIVE_MOUNTED = False
    print("⚠️ Not running in Google Colab or drive mounting failed. Will save models locally.")

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# List of 10 Transformers to compare
MODELS_TO_TRAIN = [
    "google/muril-base-cased",               # Best for Indian Languages/Tenglish
    "xlm-roberta-base",                      # Strong Multilingual
    "bert-base-multilingual-cased",          # Standard Multilingual
    "ai4bharat/indic-bert",                  # Indian Language Focus
    "distilbert-base-multilingual-cased",    # Lightweight Multilingual
    "roberta-base",                          # Monolingual Baseline
    "bert-base-uncased",                     # Monolingual Baseline
    "google/electra-small-discriminator",    # Efficient Monolingual
    "albert-base-v2",                        # Parameter Efficient
    "microsoft/deberta-base"                 # Strong Attention Mechanism
]

MAX_LEN = 128
BATCH_SIZE = 16 # Kept at 16 to prevent Out of Memory (OOM) on Colab T4 GPUs
EPOCHS = 5
LEARNING_RATE = 2e-5

# ==========================================
# 2. DATASET PREPARATION (Kaggle or Local)
# ==========================================
# NOTE: If you are using Kaggle in Colab, ensure kaggle.json is uploaded
# and run the following in a Colab cell BEFORE running this script:
# !mkdir -p ~/.kaggle
# !cp kaggle.json ~/.kaggle/
# !chmod 600 ~/.kaggle/kaggle.json
# !kaggle datasets download -d <YOUR_KAGGLE_USERNAME>/<YOUR_DATASET_NAME>
# !unzip <YOUR_DATASET_NAME>.zip

DATA_PATH = "humor_dataset_v3.csv" # Change this if your Kaggle dataset extracts to a different filename

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Please ensure it is downloaded and extracted.")

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

# Drop any nulls and ensure text is string
df = df.dropna(subset=['text', 'label'])
df['text'] = df['text'].astype(str)
df['label'] = df['label'].astype(int)

# Stratified Split: 80% Train, 10% Validation, 10% Test
print("Splitting dataset (80/10/10)...")
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])

raw_datasets = DatasetDict({
    "train": Dataset.from_pandas(train_df, preserve_index=False),
    "validation": Dataset.from_pandas(val_df, preserve_index=False),
    "test": Dataset.from_pandas(test_df, preserve_index=False)
})

print(f"Train size: {len(raw_datasets['train'])}")
print(f"Validation size: {len(raw_datasets['validation'])}")
print(f"Test size: {len(raw_datasets['test'])}")

# ==========================================
# 3. METRICS FUNCTION
# ==========================================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
    acc = accuracy_score(labels, predictions)
    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }

# ==========================================
# 4. TRAINING LOOP FOR ALL MODELS
# ==========================================
all_results = []

for model_name in MODELS_TO_TRAIN:
    print(f"\n{'='*60}")
    print(f"🚀 INITIALIZING TRAINING FOR: {model_name}")
    print(f"{'='*60}\n")
    
    try:
        # 1. Tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Ensure padding token exists (some models like ALBERT/GPT2 miss this)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        def tokenize_function(examples):
            return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=MAX_LEN)
            
        tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
        
        # 2. Model Loading
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
        
        # 3. Training Arguments
        safe_model_name = model_name.replace("/", "_")
        training_args = TrainingArguments(
            output_dir=f"./results_{safe_model_name}",
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=LEARNING_RATE,
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=BATCH_SIZE,
            num_train_epochs=EPOCHS,
            weight_decay=0.01,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            fp16=torch.cuda.is_available(), # Crucial for Colab speed (Uses Mixed Precision)
            report_to="none", # Disables WandB to prevent Colab login prompts
            logging_dir=f"./logs_{safe_model_name}",
            logging_steps=100,
        )
        
        # 4. Trainer Definition
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            compute_metrics=compute_metrics,
        )
        
        # 5. Train
        print(f"Training {model_name}...")
        trainer.train()
        
        # 6. Evaluate on Unseen TEST Set
        print(f"Evaluating {model_name} on Test Set...")
        test_metrics = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
        
        print(f"\n✅ {model_name} Final Test Metrics:")
        print(json.dumps(test_metrics, indent=4))
        
        # 6.5 Save the BEST model and tokenizer
        # (Since load_best_model_at_end=True, trainer.model is the best one)
        if DRIVE_MOUNTED:
            final_save_path = f"/content/drive/MyDrive/Tenglish_Models/{safe_model_name}"
        else:
            final_save_path = f"./final_saved_models/{safe_model_name}"
        
        print(f"💾 Saving best model & tokenizer to {final_save_path}...")
        trainer.save_model(final_save_path)
        tokenizer.save_pretrained(final_save_path)
        
        # 7. Store Results
        all_results.append({
            "Model Name": model_name,
            "Accuracy": round(test_metrics.get("eval_accuracy", 0.0) * 100, 2),
            "Precision": round(test_metrics.get("eval_precision", 0.0), 3),
            "Recall": round(test_metrics.get("eval_recall", 0.0), 3),
            "F1 Score": round(test_metrics.get("eval_f1", 0.0), 3)
        })
        
    except Exception as e:
        print(f"❌ Error training {model_name}: {str(e)}")
        all_results.append({
            "Model Name": model_name,
            "Accuracy": "ERROR",
            "Precision": "ERROR",
            "Recall": "ERROR",
            "F1 Score": "ERROR"
        })
        
    finally:
        # 8. EXTREME MEMORY CLEANUP
        # If we don't do this, Colab will crash with Out Of Memory (OOM) after 2-3 models
        print(f"Cleaning memory after {model_name}...")
        if 'model' in locals():
            del model
        if 'trainer' in locals():
            del trainer
        if 'tokenizer' in locals():
            del tokenizer
        
        torch.cuda.empty_cache()
        gc.collect()

# ==========================================
# 5. SAVE CONSOLIDATED RESULTS
# ==========================================
print("\n🎉 ALL TRAINING COMPLETE! 🎉")
results_df = pd.DataFrame(all_results)

# Sort by F1 Score if no errors occurred
if "ERROR" not in results_df["F1 Score"].values:
    results_df = results_df.sort_values(by="F1 Score", ascending=False)

csv_save_path = "all_10_models_evaluation_results.csv"
if DRIVE_MOUNTED:
    # Ensure the directory exists on Drive
    os.makedirs("/content/drive/MyDrive/Tenglish_Models", exist_ok=True)
    csv_save_path = "/content/drive/MyDrive/Tenglish_Models/all_10_models_evaluation_results.csv"

results_df.to_csv(csv_save_path, index=False)

print("\n" + "="*50)
print("FINAL LEADERBOARD")
print("="*50)
print(results_df.to_string(index=False))
print("="*50)
print(f"Results saved to '{csv_save_path}'")
