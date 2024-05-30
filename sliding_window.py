
class SlidingWindow:
    def __init__(self, window_size=256, overlap=128, tokenizer="roberta", pad_sequence_flag=True, MAX_LEN=512):
        self.window_size = window_size
        self.overlap = overlap
        self.tokenizer = tokenizer
        self.pad_sequence_flag = pad_sequence_flag
        self.MAX_LEN = MAX_LEN
        self.pad_sequence_length = self.MAX_LEN

        print("[INFO] Initializing Sliding Window Class")
        print("Window Size: ", self.window_size)
        print("Overlap: ", self.overlap)
        print("Tokenizer: ", self.tokenizer)
        print("MAX LEN: ", self.MAX_LEN)
        print("Pad Sequence Length: ", self.pad_sequence_length)

    def apply_sliding_window(self,sentences,tags):
            windowed_sentences = []
            windowed_tags = []

            for sentence, tag in zip(sentences, tags):
                tokens = sentence.split()
                label_tags = tag.split(',')

                for i in range(0, len(tokens), self.window_size - self.overlap):
                    windowed_sentences.append(tokens[i:i + self.window_size])
                    windowed_tags.append(label_tags[i:i + self.window_size])

            return windowed_sentences, windowed_tags

    def pad_sequence(self,sequence,padding_type="POST",sequence_type="input_ids",tokenizer='roberta'):
        # padding_type = ["POST","PRE"]
        # sequence_type = ["input_ids", "attention_mask"]

        if self.tokenizer == 'roberta':
            if sequence_type == "input_ids":
                padding_data = [1]
            elif sequence_type == "attention_mask":
                padding_data = [0]
        elif self.tokenizer == 'distilbert':
            if sequence_type == "input_ids":
                padding_data = [0]
            elif sequence_type == "attention_mask":
                padding_data = [0]
            

        if padding_type == "POST":
            sequence.extend(padding_data*(self.pad_sequence_length-len(sequence)))
            return sequence
        elif padding_type == "PRE":
            temp_data = [padding_data]*(self.pad_sequence_length-len(sequence))
            return temp_data

    def create_token_windows(self,tokenizer_output,labels,label_ids_flag=False):
        #windowed_output = {}
        input_ids_list = []
        attention_mask_list = []
        labels_list = []
        
        label_ids_list = self.tags_to_ids(labels)

        if self.tokenizer == "roberta":
            start_token = [0]
            end_token = [2]
        
        elif self.tokenizer == "distilbert":
            start_token = [101]
            end_token = [102]

        else:
            print("[ERROR] No Tokenizer Defined - ", self.tokenizer)
            exit()

            #print("[INFO] Tokenizer Output Classes: ", tokenizer_output.keys())

        #for index,sequence in enumerate(tokenizer_output['input_ids']):
        for index,input_sequence in enumerate(tokenizer_output):
            sequence = input_sequence['input_ids'][1:-1]
            attention_sequence = input_sequence['attention_mask'][1:-1]
            label = labels[index]

            for i in range(0,len(sequence),self.window_size - self.overlap):

                window_input_ids = sequence[i:i+self.window_size]
                window_input_ids = start_token+window_input_ids+end_token
                window_input_ids = self.pad_sequence(window_input_ids,sequence_type="input_ids",tokenizer=self.tokenizer)
                input_ids_list.append(window_input_ids)

                attention_mask = attention_sequence[i:i+self.window_size]
                attention_mask = [1]+attention_mask+[1]
                attention_mask = self.pad_sequence(attention_mask,sequence_type="attention_mask",tokenizer=self.tokenizer)
                attention_mask_list.append(attention_mask)

                if label_ids_flag == True:
                    labels_list.append(label_ids_list[label])
                else:
                    labels_list.append(label)

                #print(len(window_input_ids),i)
                #print(len(attention_mask))
        #label_ids_list = self.tags_to_ids(labels_list).values()

        return input_ids_list,attention_mask_list,labels_list

    def tags_to_ids(self,labels):
        # Initialize tagset and tag-to-index mapping
        return {t: i for i, t in enumerate(set(labels))}

