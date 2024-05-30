import pandas as pd


def split_email(text,label,index,chunk_size=250):
    textlist = text.split()
    textchunk = [' '.join(textlist[i:i+chunk_size]) for i in range(0, len(textlist), chunk_size)]
    labellist = [label]*len(textchunk)
    indexlist = [index]*len(textchunk)

    return [textchunk,labellist,indexlist]

def generate_sub_texts(df):
    textlist,labellist,indexlist = [],[],[]
    for index,row in df.iterrows():
        rowtextchunk,rowlabellist,rowindexlist = split_email(row['text'],row['label'],index)
        textlist.extend(rowtextchunk)
        labellist.extend(rowlabellist)
        indexlist.extend(rowindexlist)

    newdf = pd.DataFrame(list(zip(textlist,labellist,indexlist)),columns=['text','label','indexpos'])
    return newdf

