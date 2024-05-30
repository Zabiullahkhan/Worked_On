from pred_config import DATA_PATH, MODEL_PATH, TOKENIZER_PATH, PICKLE_FILE
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sliding_window import SlidingWindow
import preprocess as pp
import pickle
import os



class Main:
    def __init__(self):
        self.sw = SlidingWindow(window_size=256, overlap=128, tokenizer="distilbert")
        self.model_path = MODEL_PATH
        self.tokenizer_path = TOKENIZER_PATH
        self.pickle_file = PICKLE_FILE
        
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
        
        if torch.cuda.is_available():
            self.model.to(torch.device("cuda"))
            
            
    def predict(self, subject, emailBody):
        self.text = pp.preprocess_text(subject, emailBody)
        if (self.text.isspace()) or (len(self.text.strip()) < 16):
            print("Skipping text: Empty characters or too short")
            results_df = {
            'class_': "Skipping text: Empty characters or too short",
            'confidence': 0
            }
            return results_df
        else:
            self.input_tokens = self.tokenizer(self.text) #, truncation=True, padding=True, max_length=512, return_tensors='pt')
            self.input_ids, self.masks, _ = self.sw.create_token_windows([self.input_tokens], ['dummylabel'])
            self.input_ids = torch.tensor(self.input_ids, dtype=torch.long)
            self.masks = torch.tensor(self.masks, dtype=torch.long)
    
            self.input_data_list = [{'input_ids': ids, 'attention_mask': self.masks[index]} for index, ids in enumerate(self.input_ids)]
            prob_list = []
            
            with open(self.pickle_file, 'rb') as file:
                self.id2label = pickle.load(file)
    
            for inputs in self.input_data_list:
                if torch.cuda.is_available():
                    inputs = {key: value.to('cuda') for key, value in inputs.items()}
                
                logits = self.model(**inputs).logits
    
                probabilities = torch.softmax(logits, dim=1)
                prob_list.append(probabilities)
         
            mean_prob = torch.mean(torch.stack(prob_list), dim=0)
    
            predicted_class = torch.argmax(mean_prob, dim=1).item()
            confidence_score = mean_prob.max(dim=1).values.item()
            predicted_label = self.id2label[predicted_class]
    
            results_df = {
                'class_': predicted_label,
                'confidence': confidence_score
            }
    
            return results_df



