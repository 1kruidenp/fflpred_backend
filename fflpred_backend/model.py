import pandas as pd
from merge_years.import_data import get_full_data
from fflpred_backend.preprocessing import preprocess_gk
from fflpred_backend.utils import position_soyuncu
from fflpred_backend.preprocessing import split_positions
from fflpred_backend.preprocessing import preprocess_fwd
from fflpred_backend.preprocessing import preprocess_mid
from fflpred_backend.preprocessing import preprocess_def
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor
    
    
def main():

    #Get the full data set from merge_years.import_data
    data=get_full_data('raw_data')
    
    #Set the position for player named soyuncu
    data=position_soyuncu(data)

    #Split the data between train and test
    train_raw_df = data[~((data.season > 20) & (data.GW >= 38-3))]
    test_raw_df = data[(data.season > 20) & (data.GW >= 38-3)]
    
    #drop unnecessary columns
    train_raw_df.drop(columns=['fixture', 'element', 'team_a_score', 'team_h_score', 'team_id', 'team_name'],inplace=True)
    test_raw_df.drop(columns=['fixture', 'element', 'team_a_score', 'team_h_score', 'team_id', 'team_name'],inplace=True)

    #split train and test datasets in datasets per positions
    fwd_df_train,mid_df_train,def_df_train,gk_df_train=split_positions(train_raw_df)
    fwd_df_test,mid_df_test,def_df_test,gk_df_test=split_positions(test_raw_df)
    
    """FORWARDS"""
    #preprocess the forwards
    X_fwd_train, y_fwd_train, hold_fwd_train = preprocess_fwd(fwd_df_train,2)
    X_fwd_test, y_fwd_test, hold_fwd_test = preprocess_fwd(fwd_df_test,2)
    
    #train on the forwards and predict
    reg = GradientBoostingRegressor(random_state=0)
    reg.fit(X_fwd_train, y_fwd_train)
    y_fwd_pred=reg.predict(X_fwd_test)
    
    #find the mean average error
    print(f"mae for the forwards {mean_absolute_error(y_fwd_test,y_fwd_pred)}")
    
    #Create two new columns for our hold dataframe that we will return
    hold_fwd_test['predicted_points']=y_fwd_pred
    hold_fwd_test['position']=['FWD']*len(hold_fwd_test)
    
    
    """MIDFIELDERS"""
    #preprocess the midfielders
    X_mid_train, y_mid_train, hold_mid_train = preprocess_mid(mid_df_train,3)
    X_mid_test, y_mid_test, hold_mid_test = preprocess_mid(mid_df_test,3)
    
    #train on the midfielders and predict
    reg = GradientBoostingRegressor(random_state=0)
    reg.fit(X_mid_train, y_mid_train)
    y_mid_pred=reg.predict(X_mid_test)
    
    #find the mean average error
    print(f"mae for the midfielders {mean_absolute_error(y_mid_test,y_mid_pred)}")
    
    #Create two new columns for our hold dataframe that we will return
    hold_mid_test['predicted_points']=y_mid_pred
    hold_mid_test['position']=['MID']*len(hold_mid_test)
    
    """DEFENDERS"""
    #preprocess the defenders
    X_def_train, y_def_train, hold_def_train = preprocess_def(def_df_train,3)
    X_def_test, y_def_test, hold_def_test = preprocess_def(def_df_test,3)
    
    #train on the defenders and predict
    reg = GradientBoostingRegressor(random_state=0)
    reg.fit(X_def_train, y_def_train)
    y_def_pred=reg.predict(X_def_test)
    
    #find the mean average error
    print(f"mae for the defenders {mean_absolute_error(y_def_test,y_def_pred)}")
    
    #Create two new columns for our hold dataframe that we will return
    hold_def_test['predicted_points']=y_def_pred
    hold_def_test['position']=['DEF']*len(hold_def_test)
    
    """GOALKEEPERS"""
    #preprocess the goalkeepers
    X_gk_train, y_gk_train, hold_gk_train = preprocess_gk(gk_df_train,1)
    X_gk_test, y_gk_test, hold_gk_test = preprocess_gk(gk_df_test,1)
    
    #scale the goalkeepers
    scaler = MinMaxScaler()
    scaler.fit(X_gk_train)
    X_gk_train=scaler.transform(X_gk_train)
    X_gk_test=scaler.transform(X_gk_test)
    

    #train on the goalkeepers and predict
    reg = KNeighborsRegressor()
    reg.fit(X_gk_train, y_gk_train)
    y_gk_pred=reg.predict(X_gk_test)
    
    #find the mean average error
    print(f"mae for the goalkeepers KNN {mean_absolute_error(y_gk_test,y_gk_pred)}")
    
    #Create two new columns for our hold dataframe that we will return
    hold_gk_test['predicted_points']=y_gk_pred
    hold_gk_test['position']=['GK']*len(hold_gk_test)
    
    hold_list=[hold_fwd_test[hold_fwd_test.GW==38],hold_mid_test[hold_mid_test.GW==38],hold_def_test[hold_def_test.GW==38],hold_gk_test[hold_gk_test.GW==38]]
    final_list=pd.concat(hold_list)
    final_list=final_list.reset_index().drop(columns='index')

    
    print('DONNNEEEE')
    return final_list

if __name__ == "__main__":
    print(main())