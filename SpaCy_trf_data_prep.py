import json
import os

### --------------------FUNCTION TO SPLIT A SINGLE CONLL FILE IN TO A TRAIN AND DEV FILE AT PARTICULAR RATIO---------------------###
def split_conll_data(input_file, train_ratio=0.8):
    with open(input_file, 'r', encoding='utf-8') as f:
        conll_data = f.readlines()

    starting_line = ''
    counter = 0 
    for index, line in enumerate(conll_data):
        if line.startswith("-DOCSTART-"):
            starting_line += line
        elif line == '\n':
            counter += 1

    num_train_email = int(train_ratio * counter)
    counterII = 0
    for index, line in enumerate(conll_data):
        if line == '\n':
            counterII += 1
        if line == '\n' and counterII == num_train_email:
            train_data = conll_data[:index+1]
            valid_data = conll_data[index+1:]
            break 
    
    valid_data.insert(0, starting_line)

    # Get the directory path of the input_file
    directory_path = os.path.dirname(input_file)

    # Join the directory path with the filenames
    train_file = os.path.join(directory_path, 'Training_data.conll')
    
    with open(train_file, 'w', encoding='utf-8') as f_train:
        f_train.writelines(train_data)

    valid_file = os.path.join(directory_path, 'Validation_data.conll')
    
    with open(valid_file, 'w', encoding='utf-8') as f_valid:
        f_valid.writelines(valid_data)
    return train_file, valid_file


####----------------------FUNCTION TO CONVERT IN TO A SPACY SUPPORTED CONLL FORMAT ----------------------------####

def convert_conll_to_tsv(input_conll_data):
    tsv_data = []
    with open(input_conll_data, 'r', encoding = "utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('-DOCSTART-'):
                tsv_data.append(line)
                continue
            elif line == '':
                tsv_data.append('')

            elif line:
                tokens = line.split()
                if len(tokens) == 4:
                    word, _, _, label = tokens
                    tsv_data.append(f"{word.lower()}\t{label}")
                elif len(tokens) == 5:
                    word, _, _, _, label = tokens
                    tsv_data.append(f"{word.lower()}\t{label}")
                else:
                    tsv_data.append(" ")

    output_tsv_file = input_conll_data.replace(".conll", ".tsv")

    with open(output_tsv_file, "w", encoding = "utf-8") as file:
        file.write("\n".join(tsv_data))
    return output_tsv_file


#### ---------------------------- PROVIDE INPUT FILE PATH ----------------------------####
input_file = r'/home/wipro/NLP_RnD/PB_ENTITY/SpaCy_Trf_17_07_2023/FIRST_IOB_968_DATA.conll'


output_train_tsv_data = convert_conll_to_tsv(split_conll_data(input_file, train_ratio=0.8)[0])
output_dev_tsv_data = convert_conll_to_tsv(split_conll_data(input_file, train_ratio=0.8)[1])

## CONVERSION OF TSV DATA TO JSON ##
train_cmd = f"python -m spacy convert {output_train_tsv_data} ./ -t json -n 1 -c iob"
dev_cmd = f"python -m spacy convert {output_dev_tsv_data} ./ -t json -n 1 -c iob"

os.system(train_cmd)
os.system(dev_cmd)

output_train_json_data = "./Training_data.json"
output_dev_json_data = "./Validation_data.json"

## CONVERSION OF JSON TO SPACY DATA FORMAT THAT IS BINARY FORMAT ##
train_json_cmd = f"python -m spacy convert {output_train_json_data} ./ -t spacy"
dev_json_cmd = f"python -m spacy convert {output_dev_json_data} ./ -t spacy"

os.system(train_json_cmd)
os.system(dev_json_cmd)

output_train_spacy_data = "./Training_data.spacy"
output_dev_spacy_data = "./Validation_data.spacy"
