import pandas as pd
from module.cal_compatibility.asset.uma_to_xls import UMA_DATA_DICT_LIST
import json


df = pd.DataFrame(UMA_DATA_DICT_LIST)
df.to_excel('result.xlsx', index=False)
ndf = df.loc[(df['blue_factor'].str.contains('1')) & (df['red_factor'].str.contains('1')) & ~df['white_factor'].apply(lambda x: 'URA剧本' in x or '逆时针' in x)]
ndf.to_excel('remove_result.xlsx', index=False)
