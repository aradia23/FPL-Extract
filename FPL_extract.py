import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g

def calc_regression(x, y):
    n = np.size(x)
    m_x = np.mean(x)
    m_y = np.mean(y)

    SS_xx = np.sum(x * x) - n*(m_x * m_x)
    SS_xy = np.sum(y * x) - n*(m_y * m_x)

    b_1 = SS_xy/SS_xx
    b_0 = m_y - b_1*m_x

    regression = b_0 + b_1*x

    return regression

def plot_regressionline (x, y, regression,  x_label, axs, text):
    # plotting the actual points as scatter plot

    axs.scatter(x, y, color = "m", 
               marker = "o") 
  
    # plotting the regression line 
    axs.plot(x, regression, color = "g")

    axs.set_title(x_label)

    for i, txt in enumerate(text):
        axs.annotate(txt, (x[i], y[i]))

def Createfigure(title):
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.set_figheight(7)
    fig.set_figwidth(10)
    fig.suptitle(title)
    return fig, ax1, ax2, ax3

def Per90(dataframe):
    dataframe["C/90"] = (dataframe["creativity"]/dataframe["minutes"])*90
    dataframe["I/90"] = (dataframe["influence"]/dataframe["minutes"])*90
    dataframe["T/90"] = (dataframe["threat"]/dataframe["minutes"])*90
    return dataframe

def PredictedValuesColumns(dataframe, creativity, influence, threat):
    dataframe["C_predicted"] = creativity
    dataframe["I_predicted"] = influence
    dataframe["T_predicted"] = threat
    dataframe["ICT_predicted"] = (dataframe["T_predicted"] + dataframe["I_predicted"] + dataframe["C_predicted"])/3
    return dataframe

if __name__ == "__main__":
    # Retrieving Data from FPL and creating A data Frame from the Data
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    json = r.json()
    elements_df = pd.DataFrame(json["elements"])
    elements_types_df = pd.DataFrame(json["element_types"])
    teams_df = pd.DataFrame(json["teams"])

    # Creating 3 different Data frames, one which has all the players, one which is seperated by postion, one which is seperated by teams
    elements_df["position"] = elements_df.element_type.map(elements_types_df.set_index("id").singular_name)
    elements_df["team"] = elements_df.team.map(teams_df.set_index("id").name)
    elements_df["value"] = elements_df.value_season.astype(float)

    # Selecting the all the columns I want to see from the from the player Data fram 
    features = ["web_name", "team", "position", "now_cost","chance_of_playing_this_round", "minutes",
                "points_per_game", "value", "total_points", "influence", "creativity", "threat"]
    slim_elements_df = elements_df[features]

    # Converting the columns from strings to Floats
    slim_elements_df["creativity"] = slim_elements_df["creativity"].astype(float)
    slim_elements_df["influence"] = slim_elements_df.influence.astype(float)
    slim_elements_df["threat"] = slim_elements_df.threat.astype(float)

    # Selecting Players to have at least played over the 2/3rds of minutes available 
    slim_elements_df.sort_values("value",ascending=False)
    minutes_required = (2 * slim_elements_df["minutes"].max())/3
    slim_elements_df = slim_elements_df.loc[slim_elements_df.minutes > minutes_required]

    # Creating 4 new data frames, seperating each player to the postion they play 
    fwd_df = slim_elements_df.loc[slim_elements_df.position == "Forward"]
    mid_df = slim_elements_df.loc[slim_elements_df.position == "Midfielder"]
    def_df = slim_elements_df.loc[slim_elements_df.position == "Defender"]
    goal_df = slim_elements_df.loc[slim_elements_df.position == "Goalkeeper"]

    gk_lables = goal_df["web_name"].tolist()
    def_lables = def_df["web_name"].tolist()
    mid_lables = mid_df["web_name"].tolist()
    fwd_lables = fwd_df["web_name"].tolist()

    # Creatng Arrays from the Data I want to evaluate. Need to do this for each column and each Data Frame
    x_gk_creativity = np.array(goal_df["creativity"])
    x_gk_influence = np.array(goal_df["influence"])
    x_gk_threat = np.array(goal_df["threat"])
    y_gk_points = np.array(goal_df["total_points"])

    x_def_creativity = np.array(def_df["creativity"])
    x_def_influence = np.array(def_df["influence"])
    x_def_threat = np.array(def_df["threat"])
    y_def_points = np.array(def_df["total_points"])

    x_mid_creativity = np.array(mid_df["creativity"])
    x_mid_influence = np.array(mid_df["influence"])
    x_mid_threat = np.array(mid_df["threat"])
    y_mid_points = np.array(mid_df["total_points"])

    x_fwd_creativity = np.array(fwd_df["creativity"])
    x_fwd_influence = np.array(fwd_df["influence"])
    x_fwd_threat = np.array(fwd_df["threat"])
    y_fwd_points = np.array(fwd_df["total_points"])

    # Calculating the coefficients from the data Provided. Need to do this for each column and each Data Frame
    reg_gk_creativity = calc_regression(x_gk_creativity, y_gk_points)
    reg_gk_influence = calc_regression(x_gk_influence, y_gk_points)
    reg_gk_threat = calc_regression(x_gk_threat, y_gk_points)

    reg_def_creativity = calc_regression(x_def_creativity, y_def_points)
    reg_def_influence = calc_regression(x_def_influence, y_def_points)
    reg_def_threat = calc_regression(x_def_threat, y_def_points)

    reg_mid_creativity = calc_regression(x_mid_creativity, y_mid_points)
    reg_mid_influence = calc_regression(x_mid_influence, y_mid_points)
    reg_mid_threat = calc_regression(x_mid_threat, y_mid_points)

    reg_fwd_creativity = calc_regression(x_fwd_creativity, y_fwd_points)
    reg_fwd_influence = calc_regression(x_fwd_influence, y_fwd_points)
    reg_fwd_threat = calc_regression(x_fwd_threat, y_fwd_points)


    # Add new columns showing the predicted points from the creativity, influence or threat
    goal_df = PredictedValuesColumns(goal_df, reg_gk_creativity, reg_gk_influence, reg_gk_threat)
    goal_df = Per90(goal_df)
    goal_df = goal_df.round(decimals = 2)

    def_df = PredictedValuesColumns(def_df, reg_def_creativity, reg_def_influence, reg_def_threat)
    def_df = Per90(def_df)
    def_df = def_df.round(decimals = 2)

    mid_df = PredictedValuesColumns(mid_df, reg_mid_creativity, reg_mid_influence, reg_mid_threat)
    mid_df = Per90(mid_df)
    mid_df = mid_df.round(decimals = 2)

    fwd_df = PredictedValuesColumns(fwd_df, reg_fwd_creativity, reg_fwd_influence, reg_fwd_threat)
    fwd_df = Per90(fwd_df)
    fwd_df = fwd_df.round(decimals = 2)

    # Upload CSVs to Google sheets 
    SCOPES = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/apple/Downloads/fpl-data-extract-cd96fe9b6ce4.json', SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open('FPL Extract')

    d2g.upload(fwd_df, spreadsheet.id, 'Forwards', credentials=creds, row_names=True) 
    d2g.upload(mid_df, spreadsheet.id, 'Midfielders', credentials=creds, row_names=True) 
    d2g.upload(def_df, spreadsheet.id, 'Defenders', credentials=creds, row_names=True) 
    d2g.upload(goal_df, spreadsheet.id, 'Goalkeepers', credentials=creds, row_names=True) 

    # Creating plots for each position. The plot will be total_points against one of creativity, influence, threat
    fig, ax1, ax2, ax3 = Createfigure("Goalkeepers")
    plot_regressionline(x_gk_creativity, y_gk_points, reg_gk_creativity, "creativity", ax1, gk_lables)
    plot_regressionline(x_gk_influence, y_gk_points, reg_gk_influence, "Influence", ax2, gk_lables)
    plot_regressionline(x_gk_threat, y_gk_points, reg_gk_threat, "Threat", ax3, gk_lables)
    fig.tight_layout()

    fig, ax1, ax2, ax3 = Createfigure("Defenders")
    plot_regressionline(x_def_creativity, y_def_points, reg_def_creativity, "creativity", ax1, def_lables)
    plot_regressionline(x_def_influence, y_def_points, reg_def_influence, "Influence", ax2, def_lables)
    plot_regressionline(x_def_threat, y_def_points, reg_def_threat, "Threat", ax3, def_lables)
    fig.tight_layout()


    fig, ax1, ax2, ax3 = Createfigure("Midfielders")
    plot_regressionline(x_mid_creativity, y_mid_points, reg_mid_creativity, "creativity", ax1, mid_lables)
    plot_regressionline(x_mid_influence, y_mid_points, reg_mid_influence, "Influence", ax2, mid_lables)
    plot_regressionline(x_mid_threat, y_mid_points, reg_mid_threat, "Threat", ax3, mid_lables)
    fig.tight_layout()

    fig, ax1, ax2, ax3 = Createfigure("Forwards")
    plot_regressionline(x_fwd_creativity, y_fwd_points, reg_fwd_creativity, "creativity", ax1, fwd_lables)
    plot_regressionline(x_fwd_influence, y_fwd_points, reg_fwd_influence, "Influence", ax2, fwd_lables)
    plot_regressionline(x_fwd_threat, y_fwd_points, reg_fwd_threat, "Threat", ax3, fwd_lables)
    fig.tight_layout()

    plt.show()




