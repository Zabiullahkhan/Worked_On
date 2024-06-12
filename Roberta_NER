import torch
from torch.utils.data import DataLoader, Dataset
from transformers import RobertaTokenizerFast, RobertaForTokenClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
# Load the data from conll file
def read_conll(file_path):
    sentences = []
    labels = []
    sentence = []
    label = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip() == '':
                if sentence:
                    sentences.append(sentence)
                    labels.append(label)
                    sentence = []
                    label = []
            else:
                parts = line.strip().split()
                token = parts[0]
                tag = parts[-1]
                sentence.append(token)
                label.append(tag)
    if sentence:
        sentences.append(sentence)
        labels.append(label)
    return sentences, labels
sentences, labels = read_conll(r"/home/arunav/NER_RoBERTa/new_Training_data_3586.conll")
# Create a label to ID mapping
unique_labels = set(label for sublist in labels for label in sublist)
label2id = {label: idx for idx, label in enumerate(unique_labels)}
id2label = {idx: label for label, idx in label2id.items()}
# Split into train and test sets
train_texts, test_texts, train_labels, test_labels = train_test_split(
    sentences, labels, test_size=0.2, random_state=42
)
# Load the tokenizer
tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base', add_prefix_space = True)
# Tokenize the data and preserve labels
def tokenize_and_preserve_labels(texts, labels):
    tokenized_inputs = tokenizer(
        texts,
        is_split_into_words=True,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )
    labels_out = []
    for i, label in enumerate(labels):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label2id[label[word_idx]])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels_out.append(label_ids)
    tokenized_inputs["labels"] = torch.tensor(labels_out, dtype=torch.long)
    return tokenized_inputs
train_encodings = tokenize_and_preserve_labels(train_texts, train_labels)
test_encodings = tokenize_and_preserve_labels(test_texts, test_labels)
class TokenClassificationDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings
 
    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.encodings.items()}
    def __len__(self):
        return len(self.encodings['input_ids'])
 

train_dataset = TokenClassificationDataset(train_encodings)
test_dataset = TokenClassificationDataset(test_encodings)
# Load the RoBERTa model
model = RobertaForTokenClassification.from_pretrained('roberta-base', num_labels=len(label2id))
model.config.id2label = id2label
model.config.label2id = label2id
training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=1,              # number of training epochs
    per_device_train_batch_size=2,   # batch size for training
    per_device_eval_batch_size=4,    # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
    evaluation_strategy="epoch"
)
trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=test_dataset            # evaluation dataset
)
trainer.train()
results = trainer.evaluate()
print(results)
model.save_pretrained('./trained_model')
tokenizer.save_pretrained('./trained_model')




#####-----------------------CODE FOR PREDICTION----------------------####

import torch
 
from transformers import RobertaTokenizerFast, RobertaForTokenClassification
 
import json
# Load the trained model and tokenizer
 
model = RobertaForTokenClassification.from_pretrained('./trained_model')
 
tokenizer = RobertaTokenizerFast.from_pretrained('./trained_model')
# Function to make predictions on a list of sentences
 
def predict(sentences):
 
    # Tokenize the sentences
 
    tokenized_inputs = tokenizer(
 
        sentences,
 
        is_split_into_words=False,  # Because we're tokenizing plain text
 
        return_tensors="pt",
 
        padding=True,
 
        truncation=True,
 
        max_length=512,
 
        add_special_tokens=True
 
    )
    # Get predictions
 
    with torch.no_grad():
 
        outputs = model(**tokenized_inputs)
 
        logits = outputs.logits
    # Convert predictions to labels
 
    predictions = torch.argmax(logits, dim=2).numpy()
    # Get label mapping
 
    id2label = model.config.id2label
    results = []
 
    for i, sentence in enumerate(sentences):
 
        tokens = tokenized_inputs.tokens(batch_index=i)
 
        word_ids = tokenized_inputs.word_ids(batch_index=i)
 
        prediction = predictions[i]
        # Align tokens to words and labels
 
        current_word = []
 
        current_label = None
 
        entities = []
 
        for j, word_id in enumerate(word_ids):
 
            if word_id is not None:
 
                token = tokens[j]
 
                label = id2label[prediction[j]]
                if label == "O":
 
                    if current_word:
 
                        entities.append({
 
                            "entity": tokenizer.convert_tokens_to_string(current_word),
 
                            "label": current_label
 
                        })
 
                        current_word = []
 
                        current_label = None
 
                else:
 
                    if current_label and label != current_label:
 
                        entities.append({
 
                            "entity": tokenizer.convert_tokens_to_string(current_word),
 
                            "label": current_label
 
                        })
 
                        current_word = [token]
 
                        current_label = label
 
                    else:
 
                        current_word.append(token)
 
                        current_label = label
        if current_word:
 
            entities.append({
 
                "entity": tokenizer.convert_tokens_to_string(current_word),
 
                "label": current_label
 
            })
        results.append({
 
            "sentence": sentence,
 
            "entities": entities
 
        })
    return results
# Example sentences
 
sentences = [
 
    "Your account number is 1234567890 and your credit card number is 4111-1111-1111-1111.",
 
    "Please call me at 9876543210 on 10/10/2023."
 
]
# Make predictions
 
predictions = predict(sentences)
# Write predictions to a JSON file
 
with open('ner_predictions.json', 'w') as f:
 
    json.dump(predictions, f, indent=4)
