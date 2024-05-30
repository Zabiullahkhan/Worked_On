import re
import pandas as pd
##########################################____PYTHON_CODE_TO_CLEAN_SUBJECT____###########################################


def remove_thread_id_from_subject(input_text):
    input_text = input_text.lower()
    input_text = re.sub(r'[^\x00-\x7F]+', '', input_text)
    input_text = re.sub(r'\s+', ' ', input_text)
    
    parts = input_text.rsplit(':', 1)
    if len(parts) > 1:
        result = parts[1].strip()
    else:
        result = input_text
    return result


def clean_subject_line(text):
    text = re.sub(r'\s+', ' ', text)
    
    interaction_id = text.split(':')[0] 
    if len(interaction_id.split()) > 1:
        int_id = interaction_id.split()[0]
        if len(int_id) == 16:
            return text.replace(int_id, '').strip() 
        else:
            return text
    else:
        return text.replace(interaction_id, '').strip() 


def final_clean_subject(text):
    text = re.sub(r'\s+', ' ', text)
    
    set_1 = {'<.FW.>', ':<.FW.>', ':<.FW.>:', 'Reg :', ':', 'Fwd', 'Fwd :', 'Re :', 'Re', 'RE :', 'RE', 'FW :', 'FW'}
    text = re.sub(r'\??_x000D_', '', text)
    word_list= text.split()
    filtered_words = [word for word in word_list if len(word) <= 16]
    
    filtered_list_2 = [word for word in filtered_words if not any(substring in word for substring in set_1)]
    # print(filtered_list_2)
    clean_text = ' '.join(filtered_list_2)
    
    clean_text = clean_text.lstrip(':')
    
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text.strip()


##########################################____PYTHON_CODE_TO_CLEAN_EMAIL_BODY____###########################################

def remove_lines_with_keywords(text):
    keyword_tuple = (
    "external email warning",
    "do not click on any attachment",
    "use report suspicious email button to report phishing mails",
    "greetings from icici bank",
    "you dont often get email from learn why",
    "you dont often get email from",
    "customer service associate team icici bank never share your card number",
    "never share your card number, cvv, pin, otp",
    "bank employees will never ask you for these details",
    "please safeguard these account details as sharing it can lead to unauthorized access to your account",
    "this is a system generated e-mail",
    "for any further information, resident customers may write to us",
    'sent from mymail for ios',
    'print this mail only if absolutely necessary. save paper.',
    'confidentiality information and disclaimer',
    "the information contained in this electronic communication is intended solely for the individual",
    "the information contained in this e-mail and any accompanying documents may contain information that is confidential",
    "this e-mail message and its attachments may contain confidential, proprietary or legally privileged",
    'discover a new way of paying your credit card bills',
    'this is a system generated e-mail. please do not reply to this e-mail'
)
    #lines = text.split('\n')
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if not any(keyword.lower() in line.lower() for keyword in keyword_tuple):
            new_lines.append(line)
    result_text = '\n'.join(new_lines)
    return result_text

def OLD_remove_line_and_text_after_keyword(text):
    text = text.lower()
    keywords = ("adobe acrobat", "greetings from icici bank india, nri services", "you can activate your dormant account by either of the following ways")

    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        match = pattern.search(text)

        if match:
            # Remove the line containing the keyword and everything after it
            text = text[:text.rfind('\n', 0, match.start())].strip()
    return text        
def remove_line_and_text_after_keyword(text):
    text = text.lower()
    keywords = ("you require an 8-character password.", "the first four letters of your password are the first", "adobe acrobat", "greetings from icici bank india, nri services", "you can activate your dormant account by either of the following ways","print this mail only if absolutely necessary. save paper.")

    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        match = pattern.search(text)

        if match:
            # Remove the line containing the keyword and everything after it
            text = text[:text.rfind('\n', 0, match.start())].strip()
    return text.strip()

def delete_lines_from_pattern(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    pattern_22 = r'(?i)From\s*:.*?Subject\s*:'

    def remove_section(match):
        section = match.group(0)
        subject_match = re.search(r'(?i)Subject\s*:', section)
        if subject_match:
            subject_index = subject_match.start()
            return section[subject_index:]
        else:
            return section

    cleaned_text = re.sub(pattern_22, remove_section, text, flags=re.DOTALL).strip()
    
    pattern_33 = r'[-]+ forwarded message [-]+'
    cleaned_text = re.sub(pattern_33, ' ', cleaned_text).strip()
    
    pattern_34 = r'[-]+ Forwarded message [-]+'
    cleaned_text = re.sub(pattern_34, ' ', cleaned_text).strip()

    cleaned_text = re.sub(r'\S+@\S+', ' ', cleaned_text)
    
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text

def final_clean_email_body(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    special_char_tup = ('?', '|', '-', '_', '.', '>', '<', '+', '=', '*', '#', '^', '$', '@', '!', '~', '`')
    # pattern_78 = f"[{''.join(re.escape(char) for char in special_char_list)}]+"
    pattern_78 = f"({'|'.join(re.escape(char) for char in special_char_tup)})\\1+"
    text = re.sub(pattern_78, r'\1', text) 
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'"[^"]*"', '', text)
    text = text.lower()
    pattern = r'\[\s*chat\.[^\]]+\]'
    text = re.sub(pattern, '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    word_list= text.split()
    filtered_words = [word for word in word_list if len(word) <= 16]
    clean_text = ' '.join(filtered_words)

    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()


def OLD_clean_and_find_matching_extra_dates_lines(text):
    text = text.lower()
    common_pattern = re.compile(r"on\s+.*?wrote:", re.MULTILINE)
    #matching_lines = [match for match in common_pattern.findall(text) if list(datefinder.find_dates(match)) and match.endswith("wrote:")]
    matching_lines = [match for match in common_pattern.findall(text)]

    cleaned_text = text
    for matching_line in matching_lines:
        cleaned_text = cleaned_text.replace(matching_line, '')
    return cleaned_text.strip()
    
def clean_and_find_matching_extra_dates_lines(text):
    text = text.lower()

    common_pattern = re.compile(r"on\s+.*?wrote:", re.MULTILINE | re.DOTALL)
    matching_lines = [match for match in common_pattern.findall(text)]

    cleaned_text = text
    for matching_line in matching_lines:
        cleaned_text = re.sub(re.escape(matching_line), '', cleaned_text)
    return cleaned_text.strip()

def preprocess_text(subject, emailBody):
    if pd.notna(subject):
        subject = remove_thread_id_from_subject(subject)
        subject = clean_subject_line(subject)
        subject = final_clean_subject(subject)
     
    if pd.notna(emailBody):
        emailBody = remove_lines_with_keywords(emailBody)
        emailBody = clean_and_find_matching_extra_dates_lines(emailBody)
        emailBody = remove_line_and_text_after_keyword(emailBody)
       
        #emailBody = remove_headers(emailBody)
        emailBody = delete_lines_from_pattern(emailBody)
        emailBody = final_clean_email_body(emailBody)

    text = str(subject)+" "+str(emailBody) 
    return text
