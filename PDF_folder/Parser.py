import pandas as pd



df = pd.read_excel("擅長工具.xlsx")

out_dict ={}
for i in range(df.shape[0]):
    data = df.iloc[i].to_list()
    
    for _each_data in data:
        if data[0] in out_dict:
            pass
        else:
            out_dict[data[0]] ={}
        

        if data[1] in out_dict[data[0]]:
            pass
        else:
            out_dict[data[0]][data[1]] =[]

        if data[2] in out_dict[data[0]][data[1]]:
            pass
        else:
            out_dict[data[0]][data[1]].append(data[2])

import json

with open("test.txt",'w+') as file:
    file.write(json.dumps(out_dict))