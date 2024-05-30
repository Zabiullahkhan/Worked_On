import re
import calendar
import datefinder
import numpy as np
import pandas as pd
from dateutil import parser
from word2number import w2n
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DataFormatter:

    def convert_amounts(self,str_amount):
        if pd.isnull(str_amount):
            return None
        amt_dic = {
            100000: ['lacs', 'lac', 'lakhs', 'lakh', 'lk', 'lkhs'],
            1000: ['k', 'thousand'],
            10000000: ['crore', 'crores'],
            1000000:['million'],
            1000000000:['billion']
        }
        str_amount = str_amount.replace(',', '')
        pattern = r'(\d+(?:\.\d+)?)'
        matches = re.findall(pattern, str_amount)
        parts = [part for part in re.split(pattern, str_amount) if part]
        
        if len(matches) == 0:
            return None
            
        nums = matches[0]

        for j in parts:
            for i in j.split():
                for key, values in amt_dic.items():
                    i = re.sub(r'[^a-zA-Z]', '', i)
                    if i in values:
                        try:
                            nums = str(float(matches[0])*key)
                            break
                        except:
                            nums = None

        return nums
        
    def join_text_by_date_index(self,str_date):
        patterns = [r'\b\d{2,4}[./-]\d{2}[./-]\d{2,4}\b',r'\b\d{2,4}[./-]\d{2}[./-]']
        pattern_out_list = []
        for index,pat in enumerate(patterns):
            pattern_output = re.findall(pat,str_date)
            if len(pattern_output) > 0:
                if index == 1:
                    pattern_output[0] = pattern_output[0][:-1]
                pattern_out_list.append(pattern_output[0])
                break

        if pattern_out_list == []:
            return None
        else:
            return ','.join(pattern_out_list)
            
    def clean_and_parse_date(self,date_str):
        cleaned_dates = []
        if isinstance(date_str, float) or pd.isna(date_str):
            return None
        else:
            prefixes = ['on', 'dated', 'date', 'dtd','date:']
            cleaned_str = str(date_str).replace('\n', '').strip().lower()
            for prefix in prefixes:
                if cleaned_str.startswith(prefix):
                    cleaned_str = cleaned_str[len(prefix):].strip()
                    if len(cleaned_str)==0:
                        return None

            try:
                parsed_date = parser.parse(cleaned_str, fuzzy=True, dayfirst = True, default = None, ignoretz = True)
                formatted_date = parsed_date.strftime('%d-%m-%Y')   #format (e.g., 'YYYY-MM-DD')
                cleaned_dates.append(formatted_date)
                return ','.join(cleaned_dates)

            except Exception as e:
                cleaned_str_2 = self.join_text_by_date_index(cleaned_str)
                if cleaned_str_2:
                    try:
                        parsed_date = parser.parse(cleaned_str_2, fuzzy=True, dayfirst = True, default = None, ignoretz = True)
                        formatted_date = parsed_date.strftime('%d-%m-%Y')   #format (e.g., 'YYYY-MM-DD')
                        cleaned_dates.append(formatted_date)
                        return '.'.join(cleaned_dates)
                    except Exception as e:
                        return None
                else:
                    return None
                    
    def word_to_number(self,word):
        ordinals = {
            'first': 1, '1st': 1, 'second': 2, '2nd': 2, '3rd': 3, 'third': 3, 'fourth': 4, '4th': 4,
            'fifth': 5, '5th': 5, 'sixth': 6, '6th': 6, 'seventh': 7, '7th': 7, 'eighth': 8, '8th': 8,
            'ninth': 9, '9th': 9, 'tenth': 10, '10th': 10
        }
        number = ordinals.get(word.lower())
        if number is not None:
            return str(number)
        try:
            number = w2n.word_to_num(word)
            return str(number)
        except ValueError:
            return None
            
    def join_text_by_index(self,str_date):
        today = datetime.now().date()
        yy_pattern = re.findall(r'\d{2,4}',str_date)
        if len(yy_pattern) == 2 and len(yy_pattern[0])%2 == 0 and len(yy_pattern[1])%2 == 0:
            if len(yy_pattern[0]) == 4:
                start_yy = int(yy_pattern[0])
            elif len(yy_pattern[0]) == 2:
                start_yy = int(str(int(str(today.year)[0])*(10**(3-len(yy_pattern[0]))))+str(yy_pattern[0]))

            if len(yy_pattern[1]) == 4:
                end_yy = int(yy_pattern[1])
            elif len(yy_pattern[1]) == 2:
                end_yy = int(str(int(str(today.year)[0])*(10**(3-len(yy_pattern[1]))))+str(yy_pattern[1]))

            daterange = datetime(start_yy,4,1).strftime('%d-%m-%Y') + ' to ' + datetime(end_yy,3,31).strftime('%d-%m-%Y')
            return daterange

        split_val = re.split('(\d+)', str_date)
    
        index_list = []
        parse_result_list = []
    
        matching_list = ['tilltoday', 'till date', 'till today', 'till now', 'untill now', 'untill today', 'till']
        matching_pattern = '|'.join(re.escape(match) for match in matching_list)
        matching_regex = re.compile(rf'(?i)\b(?:{matching_pattern})\b')
    
        parsed_date_list = []
        month_pattern = r'(?i)jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?'
        current_date = 'to '+(datetime.now().strftime("%d-%m-%Y"))
        for i, j in enumerate(split_val):
            j = j.strip()
            exception_j_list = j.lower().split()
            matches = matching_regex.findall(j)
    
            if j.isdigit():
                parse_result_list.append(j)
                index_list.append(i) 
        
            elif re.match(month_pattern, j):
                parse_result_list.append(j)
                index_list.append(i)
        
            elif len(exception_j_list) > 1:

                for q in exception_j_list:
                    match = re.match(month_pattern, q)
                    pattern_to = r'\bto\b'
                    match_to = re.findall(pattern_to, q, re.IGNORECASE)
                
                    if match:
                        split_val[i] = split_val[i].replace(split_val[i], match.group(), 1)
                        parse_result_list.append(q)
                        index_list.append(i)
        
                    elif matches:
                        split_val[i] = split_val[i].replace(split_val[i],current_date)            
                        parse_result_list.append(q)
                        index_list.append(i)
                    elif match_to:
                        split_val[i] = split_val[i].replace(split_val[i],q)            
                        parse_result_list.append(q)
                        index_list.append(i)
          
                    elif self.word_to_number(q):
                        split_val[i] = split_val[i].replace(split_val[i], self.word_to_number(q))
                        parse_result_list.append(q)
                        index_list.append(i)
                       
            elif j.strip().lower() in matching_list:
                #split_val[i] = split_val[i].replace(split_val[i], match.group(), 1)
                split_val[i] = split_val[i].replace(split_val[i], " to ", 1)
                parse_result_list.append(j)
                index_list.append(i)

        if len(index_list)>1 and len(parse_result_list)>1:
            start_index = index_list[0]
            end_index = index_list[-1] + 1
        
            joined_text = ''.join(split_val[start_index:end_index])
            joined_text_list = joined_text.split("to")
            try:
                for i in joined_text_list:
                    parsed_date = parser.parse(i.strip(), fuzzy=True, dayfirst = True, default = None, ignoretz = True)
                    parsed_date_list.append(parsed_date.strftime("%d-%m-%Y"))
                return ' to '.join(parsed_date_list)
            except ValueError:
                return joined_text
        else:            
            return str_date

    def parse_date_fmt(self,str_date):
        if "today" in str_date or "current" in str_date:
            return datetime.now().date().strftime("%d-%m-%Y")
        elif "yesterday" in str_date:
            return (datetime.now().date() - relativedelta(days=1)).strftime("%d-%m-%Y")
        elif "tomorrow" in str_date:
            return (datetime.now().date() + relativedelta(days=1)).strftime("%d-%m-%Y")
        else:
            return None

    def check_single_date(self,str_date):
        try:
            if len(re.findall(r'\b\d{2}[-]\d{2}[-]\d{4}\b',str_date)) == 1:
                return True
            else:
                return False
        except:
            return False
        
    def extra_date_functions(self,dr):
        num_matches = re.findall(r'\d{1,4}',dr)
        num_match_len = sorted([len(i) for i in num_matches], reverse=True)

        today = datetime.now().date()
        first_day = datetime(year=today.year,month=1,day=1)
        pattern = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b"
        datepattern = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        month_dict = {'jan': 1,'feb': 2,'mar': 3,'apr': 4,'may': 5,'jun': 6,'jul': 7,'aug': 8,'sep': 9,'oct': 10,'nov': 11,'dec': 12}
        all_month_dict = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12, 'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}

        if 'yesterday' in dr or 'today' in dr:
            if 'yesterday' in dr:
                return (today - relativedelta(days=1)).strftime("%d-%m-%Y")
            else:
                return today.strftime("%d-%m-%Y")

        if len(set(num_match_len)) == 1 and num_match_len[0] == 4 and ("financial" not in dr and "fy" not in dr and "f.y" not in dr and "f y" not in dr):
            daterangelist = []
            for match in num_matches:
                daterangelist.append(datetime(int(match),1,1).date().strftime('%d-%m-%Y') + ' to ' + datetime(int(match),12,31).date().strftime('%d-%m-%Y'))
            return ', '.join(daterangelist)

        elif "year" in dr or "month" in dr or "day" in dr or "fy" in dr or "f.y" in dr or "f y" in dr or "financial" in dr:
            twonumFlag = False
            countyearFlag = False
            num_list = re.findall('[0-9]+',dr)
            if num_list == []:
                if any(word in dr for word in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']):
                    nums = w2n.word_to_num(dr)
                elif "this" in dr or "current" in dr or "present" in dr:
                    nums = 0
                else:
                    nums = 1
            else:
                if len(num_list) == 2:
                    if len(num_list[0]) == 2:
                        start_nums = int('20'+num_list[0])
                    else:
                        start_nums = int(num_list[0])
                        if "financial year" not in dr and "fy" not in dr and "f.y" not in dr and "f y" not in dr:
                            countyearFlag = True 

                    if len(num_list[1]) == 2:
                        end_nums = int('20'+num_list[1])
                    else:
                        end_nums = int(num_list[1])
                        if "financial year" not in dr and "fy" not in dr and "f.y" not in dr and "f y" not in dr:
                            countyearFlag = True 
                    twonumFlag = True

                nums = int(num_list[0])
                if len(str(nums)) >= 2:
                    nums = today.year-int("20"+str(int(nums))[-2:])
                    

            matches = re.findall(pattern,dr)
            if matches == []:
                word_month = False
            else:
                word_month = True
                for short_months in month_dict.keys():
                    if short_months in matches[0]:
                        month_number = month_dict[short_months]
            
            todayflag = False
            if "till now" in dr or "upto now" in dr or "upto" in dr or "today" in dr or "till date" in dr or "till today" in dr:
                todayflag = True

            if "year" in dr or "yr" in dr or "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                num_mt_list = re.findall(r'\d{2,4}',dr)
                if len(num_list) == 1:
                    if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                        start_date = datetime(today.year-nums,4,1)
                    else:
                        start_date = datetime(today.year-nums,1,1).date()
                else:
                    start_date = today - relativedelta(years=nums)
                    if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                        start_date = datetime(start_date.year,4,1).date()
                    else:
                        start_date = datetime(start_date.year,1,1).date()

                if twonumFlag == True and countyearFlag == False:
                    if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                        start_date = datetime(start_date.year,4,1).date()
                    else:
                        start_date = datetime(start_date.year,1,1).date()
                if todayflag == True:
                    end_date = datetime.now().date()
                else:
                    if nums == 0:
                        nums = 1
                    if len(num_list) == 1:
                        if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                            end_date = start_date + relativedelta(years=1,days=-1)
                        else:
                            end_date = datetime(start_date.year+nums-1,12,31).date()
                    else:
                        if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                            end_date = start_date + relativedelta(years=nums, days=-1)
                            end_date = datetime(end_date.year,3,31).date()
                        else:
                            end_date = datetime(start_date.year+nums-1,12,31).date()
                    if twonumFlag == True and countyearFlag == False:
                        if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                            end_date = datetime(end_nums,3,31).date()
                        else:
                            end_date = datetime(end_nums,12,31).date()

                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "month" in dr or "mnth" in dr:
                if word_month == False:
                    start_date = today - relativedelta(months=nums, days=today.day-1)
                    end_date = start_date + relativedelta(months=nums, days=-1)
                elif word_month == True:
                    start_date = today - relativedelta(months=today.month-month_number, days=today.day-1)
                    end_date = start_date + relativedelta(months=1, days=-1)
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "day" in dr and "today" not in dr:
                start_date = today - relativedelta(days=nums)
                end_date = start_date + relativedelta(days=nums)
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

        elif len(num_match_len) == 2 and ((num_match_len[0] == 4 and num_match_len[1] == 2) or (num_match_len[0] == 2 and num_match_len[1] == 2)):
            if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                start_date = datetime(int("20"+num_matches[0][-2:]),4,1)
                end_date = datetime(int("20"+num_matches[1][-2:]),3,31)
            else:
                start_date = datetime(int("20"+num_matches[0][-2:]),1,1)
                end_date = datetime(int("20"+num_matches[1][-2:]),12,31)
            return start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
        else:
            return None

    def parse_date_quarter(self,dr):
        if "quarter" in dr or "q1" in dr or "q2" in dr or "q3" in dr or "q4" in dr or "qtr" in dr:
            yr_match = re.findall(r'\b\d{2,4}\b',dr)
            for yr in yr_match:
                dr = dr.replace(yr,' ')

            start_dd = 1

            if len(yr_match) == 1:
                if '1' in dr or 'first' in dr or 'one' in dr:
                    start_mm = 1
                    end_mm = 3
                    end_dd = 31
                elif '2' in dr or 'second' in dr or 'two' in dr:
                    start_mm = 4
                    end_mm = 6
                    end_dd = 30
                elif '3' in dr or 'third' in dr or 'three' in dr:
                    start_mm = 7
                    end_mm = 9
                    end_dd = 30
                elif '4' in dr or 'four' in dr:
                    start_mm = 10
                    end_mm = 12
                    end_dd = 31
                else:
                    return None

                year = int(yr_match[0])
                start_yy = year
                end_yy = year

            elif len(yr_match) == 2:
                if '1' in dr or 'first' in dr or 'one' in dr:
                    start_mm = 4
                    end_mm = 6
                    end_dd = 30
                    start_yy = end_yy = '20'+yr_match[0][-2:]
                elif '2' in dr or 'second' in dr or 'two' in dr:
                    start_mm = 7
                    end_mm = 9
                    end_dd = 30
                    start_yy = end_yy = '20'+yr_match[0][-2:]
                elif '3' in dr or 'third' in dr or 'three' in dr:
                    start_mm = 10
                    end_mm = 12
                    end_dd = 31
                    start_yy = end_yy = '20'+yr_match[0][-2:]
                elif '4' in dr or 'four' in dr:
                    start_mm = 1
                    end_mm = 3
                    end_dd = 31
                    start_yy = '20'+yr_match[1][-2:]
                    end_yy = '20'+yr_match[1][-2:]
                else:
                    return None

            else:
                return None
            
            return datetime(int(start_yy),start_mm,start_dd).date().strftime('%d-%m-%Y') + ' to ' + datetime(int(end_yy),end_mm,end_dd).date().strftime('%d-%m-%Y')
        
        else:
            return None

    def check_date_string(self,date_string):
        skip_phrases = ['today', 'till today', 'till now', 'till date', 'every month', 'tillnow', 'upto now', 'monthly']
        datepattern = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"

        for phrase in skip_phrases:
            if phrase in date_string:
                parts = date_string.split(phrase)
                left_side = parts[0]
                if re.search(datepattern,left_side) or self.word_to_number(left_side) or len(re.findall(r'\d{1,4}',left_side)) > 0:
                    return True
                else:
                    return False
                    

            
    def parse_date_range(self,dr):
        dr = dr.lower()
        today = datetime.now().date()
        first_day = datetime(year=today.year, month=today.month, day=1)
        
        def last_day_of_date2(end_date):
            try:
                parsed_date = parser.parse(end_date)
            except ValueError:
                print("Invalid date format:", end_date)
                return None
            
            last_day = monthrange(parsed_date.year, parsed_date.month)[1]
            return parsed_date.replace(day=last_day)#.strftime('%d-%m-%Y')

        def dateiindtest(end_date):
            date21 = next(datefinder.find_dates(end_date, first='day'), None)
            date22 = next(datefinder.find_dates(end_date, strict=True, first='day'), None)
            if not (date21 and date22):
                date21 = last_day_of_date2(end_date)
            return date21

        try:
            datefin = datefinder.find_dates(dr, base_date = first_day, first = 'day', index=True)
            datelist = [[i[0].strftime('%Y-%m-%d'),dr[i[1][0]:i[1][1]]] for i in datefin]
            if len(datelist) == 2:
                print("___1___")
                start_date = datetime.strptime(datelist[0][0], '%Y-%m-%d')
                end_date = dateiindtest(datelist[1][1])
                return start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')

            elif len(datelist) == 1:
                if "since" in dr or "from" in dr:
                    start_date = datelist[0][0]
                    #print("Date_list = 2")
                    return start_date.strftime('%d-%m-%Y') + ' to ' + today.strftime('%d-%m-%Y')

        except Exception as e:
            print("NO DIRECT DATES FOUND", e)

        pattern = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b"
        datepattern = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        month_dict = {'jan': 1,'feb': 2,'mar': 3,'apr': 4,'may': 5,'jun': 6,'jul': 7,'aug': 8,'sep': 9,'oct': 10,'nov': 11,'dec': 12}

        all_month_dict = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12, 'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}

        if len(re.findall(r'\b\d{2}[-/.]\d{2}[-/.]\d{2,4}\b',dr)) == 2:
            print("___2___")
            output_date = []
            for date in re.findall(r'\b\d{2}[-/.]\d{2}[-/.]\d{2,4}\b',dr):
                date_nums = [i for i in re.split('(\d+)',date) if i.isdigit()]
                if len(date_nums[-1]) != 4:
                    date_nums[-1] = str(int(str(today.year)[0])*(10**(3-len(date_nums[-1]))))+str(date_nums[-1])
                output_date.append('-'.join(date_nums))
            return " to ".join(output_date)
        
        elif "last" in dr:
            print("___3___")
            num_list = re.findall('[0-9]+',dr)
            if num_list == []:
                if any(word in dr for word in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']):
                    nums = w2n.word_to_num(dr)
                else:
                    nums = 1
            else:
                nums = int(num_list[0])
            matches = re.findall(pattern,dr)
            if matches == []:
                word_month = False
            else:
                word_month = True
                for short_months in month_dict.keys():
                    if short_months in matches[0]:
                        month_number = month_dict[short_months]

            todayflag = False
            if "till now" in dr or "upto now" in dr or "upto" in dr or "today" in dr or "till date" in dr or "till today" in dr:
                todayflag = True

            if ("year" in dr and "month" in dr) or ("yr" in dr and "month" in dr) or ("year" in dr and "mnth" in dr) or ("yr" in dr and "mnth" in dr):

                match = re.search(r'(\d+)\s*(?:year|yr)', dr)
                years = int(match.group(1)) if match else 0
                match = re.search(r'(\d+)\s*(?:month|mnth)', dr)
                months = int(match.group(1)) if match else 0

                start_date = today - relativedelta(months=months, years=years, days=today.day-1)
                end_date = today - relativedelta(days=today.day)
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')

                return daterange
   
            elif "year" in dr or "yr" in dr or "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                if nums >= 10:
                    nums = today.year - int(num_list[0])
                
                start_date = today - relativedelta(years=nums)
                if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                    start_date = datetime(start_date.year,4,1).date()
                else:
                    start_date = datetime(start_date.year,1,1).date()
                
                end_date = start_date + relativedelta(years=nums, days=-1)
                if "financial year" in dr or "fy" in dr or "f.y" in dr or "f y" in dr:
                    end_date = datetime(end_date.year,3,31).date()
                else:
                    end_date = datetime(end_date.year,12,31).date()
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "month" in dr or "mnth" in dr:
                if word_month == False:
                    start_date = today - relativedelta(months=nums, days=today.day-1)
                    end_date = start_date + relativedelta(months=nums, days=-1)
                elif word_month == True:
                    start_date = today - relativedelta(months=today.month-month_number, days=today.day-1)
                    end_date = start_date + relativedelta(months=1, days=-1)
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange
                
            elif "day" in dr:
                start_date = today - relativedelta(days=nums)
                end_date = start_date + relativedelta(days=nums)
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "week" in dr:
                nums = nums*7
                start_date = today - relativedelta(days=nums)
                end_date = start_date + relativedelta(days=nums)
                if todayflag == True:
                    end_date = datetime.now().date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange
        
        elif "last" not in dr and "from" not in dr and "to" not in dr and "-" not in dr and "yesterday" not in dr:
            print("___4___")
            yy_pattern = re.findall(r'\d{2,4}',dr)
            if len(yy_pattern) == 2 and len(yy_pattern[0])%2 == 0 and len(yy_pattern[1])%2 == 0:
                if len(yy_pattern[0]) == 4:
                    start_yy = int(yy_pattern[0])
                elif len(yy_pattern[0]) == 2:
                    start_yy = int(str(int(str(today.year)[0])*(10**(3-len(yy_pattern[0]))))+str(yy_pattern[0]))

                if len(yy_pattern[1]) == 4:
                    end_yy = int(yy_pattern[1])
                elif len(yy_pattern[1]) == 2:
                    end_yy = int(str(int(str(today.year)[0])*(10**(3-len(yy_pattern[1]))))+str(yy_pattern[1]))

                daterange = datetime(start_yy,4,1).strftime('%d-%m-%Y') + ' to ' + datetime(end_yy,3,31).strftime('%d-%m-%Y')
                return daterange

            num_list = re.findall('[0-9]+',dr)
            if num_list == []:
                if any(word in dr for word in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']):
                    nums = w2n.word_to_num(dr)
                else:
                    nums = 1
                non_num_flag = True
            else:
                nums = int(num_list[0])
                non_num_flag = False

            matches = re.findall(pattern,dr)
            if matches == []:
                word_month = False
            else:
                word_month = True
                for short_months in month_dict.keys():
                    if short_months in matches[0]:
                        month_number = month_dict[short_months]

            if ("year" in dr and "month" in dr) or ("yr" in dr and "month" in dr) or ("year" in dr and "mnth" in dr) or ("yr" in dr and "mnth" in dr):
                
                match = re.search(r'(\d+)\s*(?:year|yr)', dr)
                years = int(match.group(1)) if match else 0
                match = re.search(r'(\d+)\s*(?:month|mnth)', dr)
                months = int(match.group(1)) if match else 0
                
                start_date = today - relativedelta(months=months, years=years, days=today.day-1)
                end_date = today - relativedelta(days=today.day)
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')

                return daterange
            
            elif "month" in dr or "mnth" in dr:
                if word_month == False:
                    if "this" in dr or "current" in dr:
                        start_date = today - relativedelta(days=today.day-1)
                        end_date = start_date + relativedelta(months=1, days=-1)
                    elif "next" in dr:
                        if today.month == 12:
                            start_mm = 1
                            start_yy = end_yy = today.year+1
                        else:
                            start_mm = today.month+1
                            start_yy = end_yy = today.year

                        end_dd = datetime(start_yy,start_mm,1).date() + relativedelta(months=1,days=-1)
                        start_date = datetime(start_yy,start_mm,1)
                        end_date = datetime(start_yy,start_mm,end_dd.day)

                    else:
                        start_date = today - relativedelta(months=nums, days=today.day-1)
                        end_date = start_date + relativedelta(months=nums, days=-1)
                    daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                    return daterange
                
                elif word_month == True:
                    patterns = re.findall(r'\d{1,4}',dr)

                    if len(patterns) == 0:
                        start_yy = today.year
                    else:
                        start_yy = int(patterns[0])

                    start_date = today - relativedelta(months=today.month-month_number, days=today.day-1)
                    start_date = start_date.replace(year=start_yy)

                    end_date = start_date + relativedelta(months=1, days=-1)
                    daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                    return daterange

            elif "annual" in dr or "financial" in dr or "fy" in dr or "f.y" in dr or "f y" in dr or "year" in dr:
                if self.extra_date_functions(dr):
                    return self.extra_date_functions(dr)
                if non_num_flag == False:
                    num_index_flag, word_index_flag = False, False
                    for i,w in enumerate(dr.split()):
                        if str(nums) in w:
                            num_index = i
                            num_index_flag = True
                        if "annual" in dr or "financial" in dr or "fy" in dr or "f.y" in dr or "f y" in dr or "year" in dr:
                            word_index = i
                            word_index_flag = True
                    if num_index_flag & word_index_flag:
                        if num_index >= word_index:
                            nums = 1

                start_date = today - relativedelta(years=nums)
                start_date = datetime(start_date.year,4,1).date()
                end_date = start_date + relativedelta(years=nums, days=-1)
                end_date = datetime(end_date.year,3,31).date()
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "day" in dr:
                start_date = today - relativedelta(days=nums)
                end_date = start_date + relativedelta(days=nums)
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "week" in dr:
                nums = nums*7
                start_date = today - relativedelta(days=nums)
                end_date = start_date + relativedelta(days=nums)
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif "quarter" in dr or "q1" in dr or "q2" in dr or "q3" in dr or "q4" in dr or "qtr" in dr:
                yr_match = re.findall(r'\b\d{2,4}\b',dr)
                for yr in yr_match:
                    dr = dr.replace(yr,' ')

                start_dd = 1

                if len(yr_match) == 1 or len(yr_match) == 0:
                    if '1' in dr or 'first' in dr or 'one' in dr:
                        start_mm = 1
                        end_mm = 3
                        end_dd = 31
                    elif '2' in dr or 'second' in dr or 'two' in dr:
                        start_mm = 4
                        end_mm = 6
                        end_dd = 30
                    elif '3' in dr or 'third' in dr or 'three' in dr:
                        start_mm = 7
                        end_mm = 9
                        end_dd = 30
                    elif '4' in dr or 'four' in dr:
                        start_mm = 10
                        end_mm = 12
                        end_dd = 31
                    else:
                        return None

                    if len(yr_match) == 0:
                        year = today.year
                    else:
                        year = int(yr_match[0])
                    start_yy = year
                    end_yy = year
                
                elif len(yr_match) == 2:
                    if '1' in dr or 'first' in dr or 'one' in dr:
                        start_mm = 4
                        end_mm = 6
                        end_dd = 30
                        start_yy = end_yy = '20'+yr_match[0][-2:]
                    elif '2' in dr or 'second' in dr or 'two' in dr:
                        start_mm = 7
                        end_mm = 9
                        end_dd = 30
                        start_yy = end_yy = '20'+yr_match[0][-2:]
                    elif '3' in dr or 'third' in dr or 'three' in dr:
                        start_mm = 10
                        end_mm = 12
                        end_dd = 31
                        start_yy = end_yy = '20'+yr_match[0][-2:]
                    elif '4' in dr or 'four' in dr:
                        start_mm = 1
                        end_mm = 3
                        end_dd = 31
                        start_yy = '20'+yr_match[1][-2:]
                        end_yy = '20'+yr_match[1][-2:]
                    else:
                        return None

                return datetime(int(start_yy),start_mm,start_dd).date().strftime('%d-%m-%Y') + ' to ' + datetime(int(end_yy),end_mm,end_dd).date().strftime('%d-%m-%Y')

                
            elif len(re.findall(pattern,dr)) > 0:
                try:
                    df_match = datefinder.find_dates(dr)
                    df_match_list = [i for i in df_match]
                    if len(df_match_list) == 1:
                        if len(re.findall(datepattern,dr)) == 1:
                            start_mm = end_mm = all_month_dict[re.findall(datepattern,dr)[0]]
                            patterns = re.findall(r'\d{1,4}',dr)
                            if len(patterns) == 0:
                                start_yy = end_yy = today.year
                            else:
                                start_yy = end_yy = 2000+int(patterns[0][-3:])
                            end_dd = (datetime(year=start_yy,month=start_mm+1,day=1)-relativedelta(days=1)).day
                            daterange = datetime(start_yy,start_mm,1).strftime('%d-%m-%Y') + ' to ' + datetime(start_yy,start_mm,end_dd).strftime('%d-%m-%Y')
                            return daterange
                        else:
                            return df_match_list[0].date().strftime('%d-%m-%Y')
                except:
                    pass

                matches = re.findall(pattern,dr)
                for short_months in month_dict.keys():
                    if short_months in matches[0]:
                        month_number = month_dict[short_months]

                dateyear = today.year

                for index,words in enumerate(dr.split()):
                    if words == matches[0]:
                        if index < len(dr.split())-1:
                            year_match = re.findall(r'\b\d{2,4}\b',dr.split()[index+1])
                            if len(year_match) > 0:
                                if len(year_match[0]) == 2:
                                    dateyear = "20"+str(year_match[0])
                                else:
                                    dateyear = year_match[0]

                start_date = today - relativedelta(months=today.month-month_number, days=today.day-1)
                start_date = start_date.replace(year=int(dateyear))
                end_date = start_date + relativedelta(months=1, days=-1)
                daterange = start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y')
                return daterange

            elif self.extra_date_functions(dr):
                return self.extra_date_functions(dr)
            
            else:
                try:
                    return parser.parse(dr, fuzzy=True, dayfirst = True, default = None, ignoretz = True).strftime("%d-%m-%Y")
                except:
                    return None
            
        elif len(re.findall(datepattern,dr)) > 1:
            print("___5___")
            try:
                df_match = datefinder.find_dates(dr,base_date=first_day)
                df_match_list = [m for m in df_match]
                print("df_match_list",df_match_list)
                if len(df_match_list) == 2:
                    print("TRY_BLOCKKKKKK")
                    date1 = df_match_list[0]
                    date2 = df_match_list[1]
                    return date1.strftime('%d-%m-%Y') + ' to ' + date2.strftime('%d-%m-%Y')
                    #return date1.datetime.strptime('%d-%m-%Y') + ' to ' + date2.datetime.strptime('%d-%m-%Y')
            except Error as e:
                print("NO DATEFINDER PRESENT : ERROR: ", e)


            matches_pos = []
            for m in re.finditer(datepattern,dr):
                matches_pos.append([m.start(0),m.end(0)])
            matches = re.findall(datepattern,dr)
            end_mm = all_month_dict[matches[1].lower()]
            mid_word = dr[matches_pos[0][1]:matches_pos[1][0]]
            pre_word = dr[:matches_pos[0][0]]
            post_word = dr[matches_pos[1][1]:]
            if pre_word == "":
                start_dd = 1
            else:
                patterns = re.findall(r'\d{1,2}',pre_word)
                if len(patterns) > 0:
                    start_dd = int(patterns[0])
                else:
                    start_dd = 1

            if mid_word == "":
                start_mm = all_month_dict[matches[0].lower()]
                if end_mm == 12:
                    end_mm,carry = 0,1
                else:
                    carry = 0
                end_dd = (datetime(year=today.year+carry,month=end_mm+1,day=1)-relativedelta(days=1)).day
                if end_mm == 0:
                    end_mm = 12
            else:
                start_mm = all_month_dict[matches[0].lower()]
                patterns = re.findall(r'\d{1,4}',mid_word)
                if len(patterns) == 0:
                    start_yy = today.year
                    if end_mm == 12:
                        end_mm,carry = 0,1
                    else:
                        carry = 0
                    end_dd = (datetime(year=today.year+carry,month=end_mm+1,day=1)-relativedelta(days=1)).day
                    if end_mm == 0:
                        end_mm = 12
                elif len(patterns) == 1:
                    mid_word = mid_word.strip()
                    if patterns[0] == mid_word[-len(patterns[0]):]:
                        end_dd = int(patterns[0])
                        start_yy = today.year
                    elif patterns[0] == mid_word[:len(patterns[0])]:
                        if len(patterns[0]) == 4:
                            start_yy = int(patterns[0])
                        else:
                            start_yy = int(str(int(str(today.year)[0])*(10**(3-len(patterns[0]))))+str(patterns[0]))
                        if end_mm == 12:
                            end_mm,carry = 0,1
                        else:
                            carry = 0
                        end_dd = (datetime(year=today.year+carry,month=end_mm+1,day=1)-relativedelta(days=1)).day
                        if end_mm == 0:
                            end_mm = 12
                    else:
                        if "to" in mid_word or "till" in mid_word or "-" in mid_word:
                            delimiters = ['to','till','-']
                            word_sep = '|'.join(map(re.escape, delimiters))
                            del_split = re.split(word_sep,mid_word)
                            if end_mm == 12:
                                end_mm,carry = 0,1
                            else:
                                carry = 0
                            if str(patterns[0]) in del_split[0]:
                                if len(patterns[0]) == 4:
                                    start_yy = int(patterns[0])
                                    end_dd = 1
                                else:
                                    start_yy = int(str(int(str(today.year)[0])*(10**(3-len(patterns[0]))))+str(patterns[0]))
                                    end_dd = (datetime(year=today.year,month=end_mm+1,day=1)-relativedelta(days=1)).day
                                    if end_mm == 0:
                                        end_mm = 12

                            elif str(patterns[0]) in del_split[1]:
                                end_dd = int(patterns[0])
                                end_yy = start_yy = today.year

                else:
                    if len(patterns[0]) == 4:
                        start_yy = int(patterns[0])
                    else:
                        start_yy = int(str(int(str(today.year)[0])*(10**(3-len(patterns[0]))))+str(patterns[0]))
                    if len(patterns[-1]) <= 2:
                        end_dd = int(patterns[-1])
                    else:
                        if end_mm == 12:
                            end_mm,carry = 0,1
                        else:
                            carry = 0
                        end_dd = (datetime(year=today.year+carry,month=end_mm+1,day=1)-relativedelta(days=1)).day
                        if end_mm == 0:
                            end_mm = 12
            
            if post_word == "":
                end_yy = today.year
            else:
                patterns = re.findall(r'\d{1,4}',post_word)
                if len(patterns) == 0:
                    end_yy = today.year
                else:
                    if len(patterns[0]) == 4:
                        end_yy = int(patterns[0])
                    else:
                        end_yy = int(str(int(str(today.year)[0])*(10**(3-len(patterns[0]))))+str(patterns[0]))

            start_dd,end_dd = self.error_handle_dates(start_dd,start_mm,start_yy,end_dd,end_mm,end_yy)
            daterange = datetime(start_yy,start_mm,start_dd).strftime('%d-%m-%Y') + ' to ' + datetime(end_yy,end_mm,end_dd).strftime('%d-%m-%Y')
            return daterange

        elif len(re.findall(datepattern,dr)) == 1:
            print("___6___")
            matches = re.findall(datepattern,dr)
            patterns = re.findall(r'\d{1,4}',dr)

            todayflag = False
            if "till now" in dr or "upto now" in dr or "upto" in dr or "today" in dr or "till date" in dr or "till today" in dr:
                try:
                    df_match = datefinder.find_dates(dr,base_date=first_day)
                    df_match_list = [m for m in df_match]
                    if len(df_match_list) == 1:
                        return df_match_list[0].strftime('%d-%m-%Y') + ' to ' + today.strftime('%d-%m-%Y')
                except:
                    print("NO DATEFINDER PRESENT")
           
            try:
                df_match = datefinder.find_dates(dr)
                df_match_list = [i for i in df_match]
                if len(df_match_list) == 1:
                    if "month" in dr:
                        start_mm = all_month_dict[matches[0]]
                        if len(patterns) == 0:
                            start_yy = today.year
                        else:
                            start_yy = int(2000+int(patterns[0][-3:]))

                        if start_mm == 12:
                            end_dd = 31
                        else:
                            end_dd = (datetime(year=start_yy,month=start_mm+1,day=1)-relativedelta(days=1)).day
                        daterange = datetime(start_yy,start_mm,1).strftime('%d-%m-%Y') + ' to ' + datetime(start_yy,start_mm,end_dd).strftime('%d-%m-%Y')
                        return daterange

                    elif len(matches) == 1:
                        start_mm = all_month_dict[matches[0]]
                        if len(patterns) == 0:
                            start_yy = today.year
                        else:
                            start_yy = int(2000+int(patterns[0][-3:]))

                        if start_mm == 12:
                            end_dd = 31
                        else:
                            end_dd = (datetime(year=start_yy,month=start_mm+1,day=1)-relativedelta(days=1)).day
                        daterange = datetime(start_yy,start_mm,1).strftime('%d-%m-%Y') + ' to ' + datetime(start_yy,start_mm,end_dd).strftime('%d-%m-%Y')
                        return daterange

                    else:
                        return df_match_list[0].date().strftime('%d-%m-%Y')
            except:
                pass

            start_mm = all_month_dict[matches[0].lower()]
            if len(patterns) == 0:
                start_yy = today.year
            else:
                start_yy = int(patterns[0])
            end_dd = (datetime(year=start_yy,month=start_mm+1,day=1)-relativedelta(days=1)).day
            daterange = datetime(start_yy,start_mm,1).strftime('%d-%m-%Y') + ' to ' + datetime(start_yy,start_mm,end_dd).strftime('%d-%m-%Y')
            return daterange
                
        else:
            print("___6___")
            if self.extra_date_functions(dr):
                return self.extra_date_functions(dr)
            elif "quarter" in dr or "q1" in dr or "q2" in dr or "q3" in dr or "q4" in dr or "qtr" in dr:
                return self.parse_date_quarter(dr)
            else:
                try:
                    return parser.parse(dr, fuzzy=True, dayfirst = True, default = None, ignoretz = True).strftime("%d-%m-%Y")
                except:
                    return None

    def error_handle_dates(self,start_dd,start_mm,start_yy,end_dd,end_mm,end_yy):
        month_last_date_dict = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
        
        if calendar.isleap(start_yy):
            month_last_date_dict[2] = 29
        if calendar.isleap(end_yy):
            month_last_date_dict[2] = 29

        if start_dd > month_last_date_dict[start_mm]:
            start_dd = month_last_date_dict[start_mm]
        if end_dd > month_last_date_dict[end_mm]:
            end_dd = month_last_date_dict[end_mm]
        return start_dd,end_dd

    def correct_mobile_number(self,text):
        pattern = r'\.$'
        text = re.sub(pattern,'',text)
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        text = url_pattern.sub('',str(text))
        l = []
        for s in text.split():
            if s.count('.') > 1 or s.count('/') > 1: 
                for j in s.split('.'):
                    if len(j) < 10:
                        pass
                    else:
                        l.append(j)           
            else:
                l.append(s)
    
        text = " ".join(l)
        text = re.sub("[^0-9\s+,/-]+", "", str(text))
        char_to_remove = '-= /'
        text = text.lstrip(char_to_remove)
        text = text.strip() 

        if text.isdigit() :
            if len(text) > 14:
                return None

        if len(text) < 10 :
            return None

        return text

    def correct_mode_of_payment(self,text):
        patterns = ['upi','gpay','neft','rtgs','imps','google pay','phonepe','amazon pay upi','net banking','credit card','paytm','payu','amazon pay','cheque']
        patterns_regex = '|'.join(r'\b{}\b'.format(re.escape(pattern)) for pattern in patterns)
        matches = re.findall(patterns_regex, text)
        match_str = ', '.join(matches)
        if match_str == '':
            return None
        else:
            return match_str
