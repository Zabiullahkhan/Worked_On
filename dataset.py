import os
import pandas as pd

class Load_Dataset:

    def datasetload(self,path):
        dflist = []

        for files in os.listdir(path):
            if files.endswith('csv'):
                df = pd.read_csv(os.path.join(path,files))
            elif files.endswith('xlsx'):
                df = pd.read_excel(os.path.join(path.files))

            dflist.append(df)
        dff = pd.concat(dflist)
        dff = dff.dropna()
        return dff
