import re
import sys
sys.path.append('./depends')
import spacy
import NER_Preprocess as pp
from NER_Postprocess import DataFormatter

dft = DataFormatter()

class Main:
    def __init__(self):
        self.model_path = "./model/model-best/"
        self.nlp = spacy.load(self.model_path)
        self.output_keys = {'account_no': 'AccountNo', 'amount': 'Amount', 'credit_card_no': 'CreditCardNo',
                            'date': 'Date', 'date_range': 'DateRange', 'deliverable_type': 'DeliverableType',
                            'mobile_no': 'MobileNo', 'mode_of_payment': 'ModeOfPayment'}
        
    def get_entity(self,subject,emailBody):
        clean_data = pp.preprocess_text(subject,emailBody)
        
        ner_labels = self.nlp.get_pipe('ner').labels
        ner_labels = set([i for i in ner_labels if i != "AMOUNTs"])
        
        doc = self.nlp(clean_data)
        
        res = [[ent.text, ent.label_, ent.start_char, ent.end_char] for ent in doc.ents]
        
        res_dict = {}
        for labels in ner_labels:
            res_dict[labels] = []
        
        for ents in res:
            res_dict[ents[1]].append(ents[0])

        formatted_dict = {}

        for ents in res_dict.keys():
            if ents == '-':
                continue
            if ents.capitalize() not in formatted_dict.keys():
                formatted_dict[ents.capitalize()] = []
            for ner_data in res_dict[ents]:
                if ents.lower() == 'date':
                    if "today" in ner_data or "tomorrow" in ner_data or "yesterday" in ner_data or "current" in ner_data:
                        try:
                            output = dft.parse_date_fmt(ner_data)
                        except:
                            continue
                    else:
                        try:
                            output = dft.clean_and_parse_date(ner_data)
                        except:
                            continue
                    
                elif ents.lower() == 'date_range':
                    try:
                        output = dft.parse_date_range(ner_data)
                    except:
                        continue
                    if output == None:
                        try:
                            output = dft.parse_date_fmt(ner_data)
                        except:
                            continue
                    elif "today" in output or "tomorrow" in output or "yesterday" in output or "current" in output:
                        try:
                            output = dft.parse_date_fmt(ner_data)
                        except:
                            continue

                    if output != None:
                        if len(re.findall(r'\b\d{2}[-]\d{2}[-]\d{4}\b',output)) == 0:
                            continue

                elif ents.lower() == 'amount':
                    try:
                        output = dft.convert_amounts(ner_data)
                    except:
                        continue
                    
                elif ents.lower() == 'mobile no':
                    try:
                        output = dft.correct_mobile_number(ner_data)
                    except:
                        continue

                elif ents.lower() == 'mode of payment':
                    try:
                        output = dft.correct_mode_of_payment(ner_data)
                    except:
                        continue
                    
                else:
                    try:
                        output = ner_data
                    except:
                        continue

                if output == None:
                    if ents.lower() == 'date_range':
                        continue
                    output = ner_data

                # check if date range produces single date
                if ents.lower() == 'date_range' and dft.check_single_date(output) == True:
                    if "Date" not in formatted_dict.keys():
                        formatted_dict["Date"] = []
                    formatted_dict["Date"].append(output)
                else:
                    formatted_dict[ents.capitalize()].append(output)

        output_dict = {self.output_keys[key.lower()]:', '.join(set(value)) for key,value in formatted_dict.items()}
        output_dict['SRNumber'] = ''
        return output_dict
        
    def predict(self,input_sub,inputStr):
        result = self.get_entity(input_sub,inputStr)
        return result

