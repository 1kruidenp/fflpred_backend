

def position_soyuncu(df):
    for i,row in df.iterrows():
        if row['name']=='caglar söyüncü':
            df['position'].at[i]='DEF'
    return df