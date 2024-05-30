import torch
import pickle
import logging
import numpy as np
import pandas as pd
import create_sub_texts as st
from dataset import Load_Dataset
from datasets import load_metric
from config import TrainingConfig
from torch.utils.data import Dataset
from sliding_window import SlidingWindow
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments #, EarlyStoppingCallback

class Main:
    def __init__(self):
        self.sw = SlidingWindow(window_size=256, overlap=128, tokenizer="distilbert")
        self.dt = Load_Dataset()
        self.logger = logging.getLogger(__name__)
        self.datasetpath = "./training_dataset"  # Update with your actual dataset path
        self.training_config = TrainingConfig()
        

    def train(self, train_directory=None, model_prefix='model'):
        if train_directory:
            self.datasetpath = train_directory

        df = self.dt.datasetload(self.datasetpath)
        print('[INFO] Dataset Loaded')
        
        #df = df.groupby('label').apply(lambda x: x.sample(300)).reset_index(drop=True) # For Testing the whole code on a small data

        df['encoded_label'] = df['label'].astype('category').cat.codes
        NUM_LABELS = len(df['encoded_label'].value_counts().index)
        print('[INFO] Preprocessing Completed')

        ids2label = dict(zip(df['encoded_label'], df['label']))
        print(ids2label)

        with open('./model/ids2label.pickle', 'wb') as fp:  # Update with the actual path
            pickle.dump(ids2label, fp)

        NUM_LABELS = len(df.label.unique())
        train_texts, val_texts, train_labels, val_labels = train_test_split(df.text.tolist(), df.encoded_label.tolist(), test_size=0.2, random_state=42)
        print('[INFO] Dataset Splitted')

        train_df = pd.DataFrame(list(zip(train_texts, train_labels)), columns=['text', 'label'])
        test_df = pd.DataFrame(list(zip(val_texts, val_labels)), columns=['text', 'label'])
        train_df = st.generate_sub_texts(train_df)
        test_df = st.generate_sub_texts(test_df)
        print('[INFO] Texts splitting completed')

        model_checkpoint = 'distilbert-base-uncased'
       # model_checkpoint = "./pretrained_model"  #pretrained model file


        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=NUM_LABELS)
        print('[INFO] Tokenizer and Model Loaded')

        # Tokenize the data
        print("[INFO] Creating embedding tokens")
        train_encodings = tokenizer(train_df.text.tolist())
        test_encodings = tokenizer(test_df.text.tolist())

        train_df['input_ids'] = train_encodings['input_ids']
        train_df['attention_mask'] = train_encodings['attention_mask']
        test_df['input_ids'] = test_encodings['input_ids']
        test_df['attention_mask'] = test_encodings['attention_mask']

        def merge_ids_lists(series):
            return [101]+[elem for sublist in series for elem in sublist[1:-1]]+[102]

        def merge_masks_lists(series):
            return [1]+[elem for sublist in series for elem in sublist[1:-1]]+[1]

        def merge_labels(series):
            return list(set(series))[0]

        print('[INFO] Merging Tokens')

        grouped_train_df = train_df.groupby('indexpos').agg({'text':' '.join,'input_ids':merge_ids_lists,'attention_mask':merge_masks_lists,'label':merge_labels}).reset_index()
        grouped_test_df = test_df.groupby('indexpos').agg({'text': ' '.join, 'input_ids':merge_ids_lists,'attention_mask':merge_masks_lists,'label':merge_labels}).reset_index()
        
        train_tokenized_dict = [{"input_ids": ids, "attention_mask": mask} for ids, mask in zip(grouped_train_df['input_ids'], grouped_train_df['attention_mask'])]
        test_tokenized_dict = [{"input_ids": ids, "attention_mask": mask} for ids, mask in zip(grouped_test_df['input_ids'], grouped_test_df['attention_mask'])]
        
        print("[INFO] Creating Sliding Windows")
        
        train_encodings,train_masks,train_labels = self.sw.create_token_windows(train_tokenized_dict,grouped_train_df['label'])
        val_encodings,val_masks,val_labels = self.sw.create_token_windows(test_tokenized_dict,grouped_test_df['label'])
        
        print('[INFO] Training Dataset Slides - ', len(train_encodings))
        print('[INFO] Testing Dataset Slides - ', len(val_encodings))
        
        train_encodings = torch.tensor(train_encodings,dtype=torch.long)
        train_masks = torch.tensor(train_masks,dtype=torch.long)
        train_labels = torch.tensor(train_labels,dtype=torch.long)
        
        val_encodings = torch.tensor(val_encodings,dtype=torch.long)
        val_masks = torch.tensor(val_masks,dtype=torch.long)
        val_labels = torch.tensor(val_labels,dtype=torch.long)

        class CustomDataset(Dataset):
            def __init__(self, input_ids, attention_mask, labels):
                self.input_ids = input_ids
                self.attention_mask = attention_mask
                self.labels = labels
        
            def __len__(self):
                return len(self.labels)
        
            def __getitem__(self, idx):
                item = {
                    'input_ids': self.input_ids[idx],
                    'attention_mask': self.attention_mask[idx],
                    'labels': self.labels[idx]
                }
                return item


        metric = load_metric("accuracy")
        f1_metric = load_metric("f1")
        
        def compute_metrics(eval_pred):
            logits, labels = eval_pred
            predictions = np.argmax(logits, axis=-1)
            accuracy = metric.compute(predictions=predictions, references=labels)
        
            # Calculate F1 score for multi-class classification (macro-average)
            f1 = f1_metric.compute(predictions=predictions, references=labels, average="macro")
            return {
                "accuracy": accuracy["accuracy"],
                "f1": f1['f1']
            }
        
        print('[INFO] Creating Custom Dataset Loader')
        
        train_dataset = CustomDataset(train_encodings, train_masks, train_labels)
        val_dataset = CustomDataset(val_encodings, val_masks, val_labels)
        
        print('[INFO] Beggining Training')

        training_args = TrainingArguments(
            output_dir = self.training_config.OUTPUT_DIR,
            num_train_epochs = self.training_config.NUM_TRAIN_EPOCHS,
            per_device_train_batch_size = self.training_config.PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size = self.training_config.PER_DEVICE_EVAL_BATCH_SIZE,
            load_best_model_at_end = self.training_config.LOAD_BEST_MODEL_AT_END,
            warmup_steps = self.training_config.WARMUP_STEPS,
            weight_decay = self.training_config.WEIGHT_DECAY,
            logging_dir = self.training_config.LOGGING_DIR,
            evaluation_strategy = self.training_config.EVALUATION_STRATEGY,
            eval_steps = self.training_config.EVAL_STEPS,
            logging_steps = self.training_config.LOGGING_STEPS,
            )


        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
            #callbacks = [EarlyStoppingCallback(early_stopping_patience=4)]
        )
        
        trainer.train()
        
        # Log the training output
        for line in trainer.state.log_history:
            self.logger.info(line)
        
        results = trainer.evaluate()
        
        model.save_pretrained('./model')
        tokenizer.save_pretrained('./model')
        
        print("-_-_"*18,f"Distill_BERT MODEL OF {self.training_config.NUM_TRAIN_EPOCHS} EPOCH HAS BEEN TRAINED", "-_-_"*18)

