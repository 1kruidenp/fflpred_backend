from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from transfer import transfer_suggestion
from pydantic import BaseModel
from google.cloud import storage
import requests

class Item(BaseModel):
    team_list: list
    budget: float

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

"""
BUCKET_NAME='wagon-613-fflpred'
STORAGE_LOCATION='predictions/predictions'
def load_model_from_gcp():
    
    client = storage.Client() # credentials input?
    
    bucket = client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(STORAGE_LOCATION)

    blob.download_to_filename('predictions.csv')"""

@app.get("/")
def index():
    return {"greeting": "Hello world! Welcome to our Fantasy Football Predictor"}


def get_best_11(df,week=38):
    best_15=df[df.GW==week]
    best_11=best_15.head(0).copy()
    sub_4=best_15.head(0).copy()
    best_11=pd.concat([best_11,best_15[best_15.position=='GK'].sort_values('predicted_points',ascending=False).head(1)])

    best_11=pd.concat([best_11,best_15[best_15.position=='DEF'].sort_values('predicted_points',ascending=False).head(3)])

    captain=best_15.sort_values('predicted_points',ascending=False).head(1).name.unique()[0]
    vice_captain=best_15.sort_values('predicted_points',ascending=False).head(2).name.unique()[1]

    for i,row in best_15.sort_values('predicted_points',ascending=False).iterrows():
        row=pd.DataFrame([row])
        if len(best_11)<11:
            if row.name.unique()[0] in best_11.name.unique():
                continue
            elif row.position.unique()[0] == 'GK':
                sub_4=pd.concat([sub_4,row])
                continue
            else:
                best_11=pd.concat([best_11,row])
        elif row.name.unique()[0] in best_11.name.unique():
                continue
        elif len(best_11)==11 and len(sub_4)<4:
            sub_4=pd.concat([sub_4,row])

    return best_11, sub_4, captain, vice_captain

"""
@app.get("/predict")
def predict(list,budget): 
    #df is 2 columns (player_name, position) of 15 rows (15 players)
    #df is a float value
    print(type(list))
    assert(len(list)==15)
    assert(type(budget)==float)
    
    all_predicted_players=main()
    all_predicted_players.drop_duplicates(inplace=True)

    player_list=pd.DataFrame(all_predicted_players.head(0))
    for player in list:
        player_list=pd.concat([player_list,all_predicted_players[all_predicted_players.name==player]])

    best_transfers=transfer_suggestion(player_list[['name','position']],budget,all_predicted_players)
    
    best_11, sub_4, captain, vice_captain = get_best_11(player_list)
    
    best_transfers=best_transfers[['name','incoming_player','points_difference']].to_dict
    
    dict_best_11=best_11[['name','position']].to_dict
    dict_sub_4=sub_4[['name','position']].to_dict
    
    
    return {'best_11':dict_best_11, 
            'subs_4':dict_sub_4,
            'captain':captain,
            'vice_captain':vice_captain,
            'best_transfers':best_transfers}
"""


@app.post("/give_prediction")
def give_prediction(input:Item):
    #df is 2 columns (player_name, position) of 15 rows (15 players)
    #df is a float value
    #load_model_from_gcp()
    

    
    
    team_list=input.team_list
    print(type(team_list))
    assert(len(team_list)==15)
    budget=input.budget
    assert(type(budget)==float)
    
    #all_predicted_players=main()
    url='https://storage.googleapis.com/wagon-613-fflpred/predictions/predictions'
    all_predicted_players=pd.read_csv(url)
    all_predicted_players.drop_duplicates(inplace=True)

    player_list=pd.DataFrame(all_predicted_players.head(0))
    for player in team_list:
        player_list=pd.concat([player_list,all_predicted_players[all_predicted_players.name==player]])

    best_transfers=transfer_suggestion(player_list[['name','position']],budget,all_predicted_players)
    
    best_11, sub_4, captain, vice_captain = get_best_11(player_list)
    
    dict_best_transfers=best_transfers[['leaving_player','incoming_player','points_difference']].to_dict()
    
    dict_best_11=best_11[['name','position']].to_dict()
    dict_sub_4=sub_4[['name','position']].to_dict()

    
    
    return {'best_11':dict_best_11, 
            'subs_4':dict_sub_4,
            'captain':captain,
            'vice_captain':vice_captain,
            'best_transfers':dict_best_transfers}
    

@app.get("/players")
def players():
    return {'players'}
        
    