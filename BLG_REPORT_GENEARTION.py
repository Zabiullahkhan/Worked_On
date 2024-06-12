# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 12:15:56 2022

@author: ZA40142720
"""
# ALL FUNCTIONS 


import os
import tabula
import pandas as pd
import warnings
warnings.filterwarnings('ignore') 
import re
from dateutil.parser import parse







def is_date(string, fuzzy=False):        # Function To check that a value is in Date Format or not

    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    
                                    # Function To Validate The Amount

def validate_amount(text):
    text = re.sub("[^0-9.]+", "",text)
    try:
        text = float(text)
        return True
    except:
        return False
                                #     Function To Clean The Amount
def clean_amount(text):
    return float(re.sub("[^0-9.]+", "",text))
                                    
                                    # Function To Clean The Date
def clean_date(text):
    return re.sub("[\r\n\t.,]", " ", text)

                                # Function To Parse The Date in to a Particular Date  Format to avoid Multi date Format
    

def date_parse(str_date):
     return parse(str_date,dayfirst=True).date()
                            #     Function to get the amount day Wise
        
def get_day_amount(day_no,daylist,lastamtval, date_amt_dict):
       
    if lastamtval == 0 and daylist !=[]:
        if day_no != 'last_day':
            expected_daylist = [str(i) for i in daylist if int(i) < int(day_no)]
            if expected_daylist == []:
                return 0
            else:
                str_daylist = daylist[expected_daylist.index(expected_daylist[-1])]
                return date_amt_dict[str_daylist]
        else:
            return date_amt_dict[sorted(daylist)[-1]]
            
    if daylist == [] and lastamtval == 0:
        return 0
    if daylist == [] and lastamtval != 0:
        return lastamtval
    if day_no in daylist:
        return date_amt_dict[day_no]
    if day_no =='last_day':
        return date_amt_dict[sorted(daylist)[-1]]
            
    int_daylist = [int(i) for i in daylist]
    expected_daylist = [str(i) for i in int_daylist if i < int(day_no)]
    
    if expected_daylist == []:
        return lastamtval
    else:
        str_daylist = daylist[expected_daylist.index(expected_daylist[-1])]
        return date_amt_dict[str_daylist]
        
    
                                """ EXCEPTIONAL PDF """  
                                
def exceptional_type_pdf(main_path):
    
    tabula.convert_into(main_path, f"C:/Users/ZA40142720/Documents/Pdf_Extraction/Exception_output/bank_st_output.csv", output_format="csv", pages='all')
    
    dfs=pd.read_csv(f"C:/Users/ZA40142720/Documents/Pdf_Extraction/Exception_output/bank_st_output.csv")
    date_list=[]
    balance_list=[]
    for row in dfs.values.tolist():
    #     print(row)
        if row==[]:
            continue
        if type(row[0]) == float or type(row[-1]) == float:
            continue
    #     print(row)
        if is_date(row[0].split(' ')[0])==True and validate_amount(row[-1])==True:  # row[0].split(' ')[0]
            amt = clean_amount(row[-1])
            cl_date = clean_date(row[0].split(' ')[0]) # row[0].split(' ')[0]
            final_date = date_parse(cl_date)
            date_list.append(str(final_date))
            balance_list.append(amt)
        else:
             continue
    
    
    df=pd.DataFrame(zip(date_list,balance_list),columns=['Date','Balance'])
    elem=df.values.tolist()
    date_dict={}
    for r in elem:
        if r[0].split('-')[0] not in date_dict.keys():
            date_dict[r[0].split('-')[0]] = {}
            date_dict[r[0].split('-')[0]][r[0].split('-')[1]] = {}
            date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1]
        else:
            if r[0].split('-')[1] not in date_dict[r[0].split('-')[0]].keys():
                date_dict[r[0].split('-')[0]][r[0].split('-')[1]] = {}
                date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1]
            else:
                date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1] 



    
    yearslist = list(date_dict.keys())
    yearslist = sorted(yearslist)
    lastamtval = 0
    counter = 0
    expected_dict = {}

    amtval_10 = 0
    amtval_20 = 0

    final_dict = {}
    month_dict={'01':'JAN','02':'FEB','03':'MAR','04':'APR','05':'MAY','06':'JUNE','07':'JULY','08':'AUG','09':'SEP','10':'OCT','11':'NOV','12':'DEC'}

    for  years in yearslist:
        final_dict[years] = {}
        monthslist = list(date_dict[years].keys())
        monthslist = sorted(monthslist)

        for month in monthslist:
            final_dict[years][month_dict[month]] = {}
            dayslist = list(date_dict[years][month].keys())
            dayslist = sorted(dayslist)

            if [i for i in dayslist if int(i) <= 10] == []:
                amtval_10 = lastamtval
                amtval_20 = lastamtval

            for index,day in enumerate(dayslist):

                if int(day)<=10:                
                    amtval_10 = get_day_amount('10',dayslist,lastamtval,date_dict[years][month])
                    amtval_20 = amtval_10
                    amtval_last = amtval_10
                elif int(day)<=20:
                    amtval_20 = get_day_amount('20',dayslist,lastamtval,date_dict[years][month])
                    amtval_last = amtval_20
                else: 
                    amtval_last = get_day_amount('last_day',dayslist,lastamtval,date_dict[years][month])
                counter+=1
                lastamtval = date_dict[years][month][day]

            final_dict[years][month_dict[month]]['BALANCE AS ON 10TH'] = float(amtval_10)/1000000
            final_dict[years][month_dict[month]]['BALANCE AS ON 20TH'] = float(amtval_20)/1000000
            final_dict[years][month_dict[month]]['BALANCE AS ON LAST DAY'] = float(amtval_last)/1000000
            final_dict[years][month_dict[month]]['AVG BALANCE'] = (float(amtval_10)+float(amtval_20)+float(amtval_last))/3000000

    # print(final_dict)
    df=pd.DataFrame.from_dict(
    {(i, j): final_dict[i][j] for i in final_dict.keys() for j in final_dict[i].keys()},
    orient="columns",)

    df['','TOTAL']=df.iloc[:,:].sum(axis=1)

    # df.to_excel(f"report{str(k)}.xlsx")
    return df.to_excel(f"C:/Users/ZA40142720/Desktop/stmnt_report/{path}_Exc___report_{str(k)}.xlsx")




                                 
                                     ''' MAIN CODE '''


list_of_files = os.listdir(r"C:/Users/ZA40142720/Documents/Pdf_Extraction/acount_statements/Multi_Type/")
for k,path in enumerate(list_of_files):
    if path.split('.')[-1].lower() != 'pdf':
        continue
    main_path = f"C:/Users/ZA40142720/Documents/Pdf_Extraction/acount_statements/Multi_Type/{path}"
    dfs = tabula.read_pdf(main_path, pages='all', lattice=True)

                                         #     Extraction of Date and Balance form the extracted pdf i.e (dfs)
    
    date_list=[]
    balance_list=[]
    for df in dfs:
        df=df.dropna(axis=1, how='all')
        for row in df.values.tolist():
            if row==[]:
                continue
    #         print(row)
            if is_date(row[0])==True and validate_amount(row[-1])==True:
                amt = clean_amount(row[-1])
                cl_date = clean_date(row[0])
                final_date = date_parse(cl_date)
                date_list.append(str(final_date))
                balance_list.append(amt)
            else:
                continue
    
    if len(date_list)==0 and len(balance_list)==0:
        exceptional_type_pdf(main_path)              # EXCEPTIONAL PDF 
    else:

        
                                         #     Creating a Pandas Data Frame from the two lists Date_lis, Balance_list
    
        df=pd.DataFrame(zip(date_list,balance_list),columns=['Date','Balance'])
    
                                         #     Creating a Dictionary of values into accoriding to year, month, day
    
        elem=df.values.tolist()
        date_dict={}
        for r in elem:
            if r[0].split('-')[0] not in date_dict.keys():
                date_dict[r[0].split('-')[0]] = {}
                date_dict[r[0].split('-')[0]][r[0].split('-')[1]] = {}
                date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1]
            else:
                if r[0].split('-')[1] not in date_dict[r[0].split('-')[0]].keys():
                    date_dict[r[0].split('-')[0]][r[0].split('-')[1]] = {}
                    date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1]
                else:
                    date_dict[r[0].split('-')[0]][r[0].split('-')[1]][r[0].split('-')[-1]] = r[1] 
    
                                             #     Logic of Report Generation
        yearslist = list(date_dict.keys())
        yearslist = sorted(yearslist)
        lastamtval = 0
        counter = 0
        expected_dict = {}

        amtval_10 = 0
        amtval_20 = 0
    
        final_dict = {}
        month_dict={'01':'JAN','02':'FEB','03':'MAR','04':'APR','05':'MAY','06':'JUNE','07':'JULY','08':'AUG','09':'SEP','10':'OCT','11':'NOV','12':'DEC'}
    
    
        for  years in yearslist:
            final_dict[years] = {}
            monthslist = list(date_dict[years].keys())
            monthslist = sorted(monthslist)
        
            for month in monthslist:
                final_dict[years][month_dict[month]] = {}
                dayslist = list(date_dict[years][month].keys())
                dayslist = sorted(dayslist)
        
                if [i for i in dayslist if int(i) <= 10] == []:
                    amtval_10 = lastamtval
                    amtval_20 = lastamtval
            
                for index,day in enumerate(dayslist):
    
                    if int(day)<=10:                
                        amtval_10 = get_day_amount('10',dayslist,lastamtval,date_dict[years][month])
                        amtval_20 = amtval_10
                        amtval_last = amtval_10
                    elif int(day)<=20:
                        amtval_20 = get_day_amount('20',dayslist,lastamtval,date_dict[years][month])
                        amtval_last = amtval_20
                    else: 
                        amtval_last = get_day_amount('last_day',dayslist,lastamtval,date_dict[years][month])
                    counter+=1
                    lastamtval = date_dict[years][month][day]
                   
                final_dict[years][month_dict[month]]['BALANCE AS ON 10TH'] = float(amtval_10)/1000000
                final_dict[years][month_dict[month]]['BALANCE AS ON 20TH'] = float(amtval_20)/1000000
                final_dict[years][month_dict[month]]['BALANCE AS ON LAST DAY'] = float(amtval_last)/1000000
                final_dict[years][month_dict[month]]['AVG BALANCE'] = (float(amtval_10)+float(amtval_20)+float(amtval_last))/3000000

        df=pd.DataFrame.from_dict(
        {(i, j): final_dict[i][j] for i in final_dict.keys() for j in final_dict[i].keys()},
        orient="columns",)
    
        df['','TOTAL']=df.iloc[:,:].sum(axis=1)

        df.to_excel(f"C:/Users/ZA40142720/Desktop/stmnt_report/{path}_report_{str(k)}.xlsx")
    #     df.to_excel("report.xlsx")
        print(f"C:/Users/ZA40142720/Desktop/stmnt_report/{path}_report_{str(k)}.xlsx")   
