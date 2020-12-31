import os
import pandas as pd
data=pd.read_csv("data.csv")

data=data.append({"name":"andres", "stack":1000, "password":"password"}, ignore_index=True)
data.to_csv(r"c:\Users\VIE ShareWizMe\Desktop\CPES L2\Algo\Projet poker\Poker\server\data.csv", index=False)

print(data)