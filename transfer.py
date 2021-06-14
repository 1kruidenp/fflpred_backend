import pandas as pd

def transfer_suggestion(team, budget, prediction):
    """
        Function to calculate the best possible transfers based on the user's current team and remaining budget.
        IN: team (list/dictionary/dataframe), budget (float), prediction (pandas dataframe)
        OUT: best transfer (pandas dataframe with top 3 transfers:
                columns: name outgoing, name incoming, remaining budget, potential point increase)
    """

    # TODO: create dataframe with team and prediction
    team_df = team.copy()

    team_df['predicted_points'] = team_df.apply(lambda row: prediction.predicted_points[prediction.name == row.name].item())

    team_df['value'] = team_df.apply(lambda row: prediction.value[prediction.name == row.name].item())

    team_df['max_budget'] = team_df.apply(lambda row: row.value + budget)


    # TODO: sort prediction by predicted score
    sorted_prediction = prediction.sort_values(by = 'predicted_points', ascending = False)
    drop_team = sorted_prediction[sorted_prediction.player.isin(team_df.name.values)].index
    sorted_prediction.drop(index = drop_team, inplace = True)

    # TODO: calculate best affordable transfer for each player
    team_df['incoming'] = 'no transfer'
    team_df['incoming_points'] = 0
    team_df['remaining_budget'] = team_df.max_budget

    for team_index, team_row in team_df.iterrows():
        for predict_index, predict_row in sorted_prediction.interrows():
            if team_row.position == predict_row.position\
                and team_row.predicted_points < predict_row.predicted_points\
                and team_row.max_budget > predict_row.value:
                    team_df.loc[team_index, 'incoming'] = predict_row.player
                    team_df.loc[team_index, 'incoming_points'] = predict_row.predicted_points
                    team_df.loc[team_index, 'remaining_budget'] = team_row.max_budget - predict_row.value

    team_df['points_difference'] = team_df.incoming_points - team_df.predicted_points

    # TODO: add top 3 transfers to a list with outgoing player, incoming player & potential points increase
    best_transfers = team_df.sort_values(by = 'points_difference', ascending = False)[['name', 'incoming', 'points_difference', 'remaining_budget']]


    return best_transfers
