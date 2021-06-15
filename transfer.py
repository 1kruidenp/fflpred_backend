import pandas as pd
from fflpred_backend.model import main

def transfer_suggestion(team, budget, prediction):
    """
        Function to calculate the best possible transfers based on the user's current team and remaining budget.
        IN: team (list/dictionary/dataframe), budget (float), prediction (pandas dataframe)
        OUT: best transfer (pandas dataframe with top 3 transfers:
                columns: name outgoing, name incoming, remaining budget, potential point increase)
    """

    # TODO: copy and clean team_df to work in locally
    team_df = team.copy()

    team_df['name'] = team_df.apply(lambda row: row['name'].lower(), axis = 1)

    # TODO: drop duplicates in prediction df
    drop_duplicates = prediction[prediction['name'].duplicated()].index
    prediction.drop(index = drop_duplicates, inplace = True)
    prediction.value = prediction.apply(lambda row: row.value / 10, axis = 1)

    # TODO: check if all team players are in prediction df
    assert (team_df['name'].isin(prediction['name'])).all()\
                ,"Not all team players in prediction dataset"

    # TODO: add predictions, player values and budget to team_df
    team_df['predicted_points'] = team_df.apply(lambda row: \
            prediction.predicted_points[prediction['name'] == row['name']].item()\
            , axis = 1)

    team_df['value'] = team_df.apply(lambda row: prediction.value[prediction['name'] == row['name']].item(), axis = 1)

    team_df['max_budget'] = team_df.apply(lambda row: row.value + budget, axis = 1)

    # TODO: sort prediction by predicted score
    sorted_prediction = prediction.sort_values(by = 'predicted_points', ascending = False)
    drop_team = sorted_prediction[
                    sorted_prediction['name'].isin(team_df['name'].values)
                    ].index
    sorted_prediction.drop(index = drop_team, inplace = True)

    # TODO: calculate best affordable transfer for each player
    team_df['incoming_player'] = 'no transfer'
    team_df['incoming_points'] = 0
    team_df['remaining_budget'] = team_df.max_budget

    for team_index, team_row in team_df.iterrows():
        for predict_index, predict_row in sorted_prediction.iterrows():
            if team_row.position == predict_row.position\
                and team_row.predicted_points < predict_row.predicted_points\
                and team_row.max_budget > predict_row.value:
                team_df.loc[team_index, 'incoming_player'] = predict_row['name']
                team_df.loc[team_index, 'incoming_points'] = predict_row.predicted_points
                team_df.loc[team_index, 'remaining_budget'] = team_row.max_budget - predict_row.value
                break

    team_df['points_difference'] = team_df.incoming_points - team_df.predicted_points


    # TODO: add top 3 transfers to a list with outgoing player, incoming player & potential points increase
    best_transfers = team_df.sort_values(by = 'points_difference', ascending = False)\
                    [['name',
                      'incoming_player',
                      'position',
                      'points_difference',
                      'remaining_budget'
                      ]].head(3).reset_index(drop=True)
    best_transfers = best_transfers.rename(columns={'name': 'leaving_player'})

    return best_transfers

if __name__=="__main__":
    prediction = main()
    team = pd.DataFrame({
        'name': [
            'Harry kane',
            'Neal maupay',
            'heung-min son',
            'adam lallana',
            'stuart Dallas',
            'matt Targett',
            'Hugo lloris'
        ],
        'position': [
            'FWD',
            'FWD',
            'MID',
            'MID',
            'DEF',
            'DEF',
            'GK'
        ]
    })

    best_transfers = transfer_suggestion(team, 4.2, prediction)
    print(best_transfers)
