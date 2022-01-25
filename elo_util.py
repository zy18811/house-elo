import pandas as pd
import pickle
import os
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

id = os.environ['DRIVE_ID']
creds = os.environ['GOOGLE_APPLICATION_CREDENTIALS']

gauth = GoogleAuth()
scope = ["https://www.googleapis.com/auth/drive"]
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(creds, scope)
drive = GoogleDrive(gauth)


def reset_df(starting_elo=1000):
    elo_df = pd.DataFrame(columns=['Sam','Luca','Amy','Gabriel'], dtype=pd.Float64Dtype)
    elo_df.loc[0] = starting_elo
    save_elo_df(elo_df)


def add_player(name):
    elo_df = get_elo_df()
    elo_df[name] = 1000
    save_elo_df(elo_df)


def elo_update(player_a, player_b, score_a, score_b):
    k = 32  # what USCF uses for <2100

    elo_df = get_elo_df()
    r_a = elo_df[player_a].iloc[-1]
    r_b = elo_df[player_b].iloc[-1]

    Q_a = 10**(r_a/400)
    Q_b = 10**(r_b/400)

    E_a = Q_a/(Q_a+Q_b)
    E_b = Q_b/(Q_a+Q_b)

    r_a += int(k*(score_a-E_a))
    r_b += int(k*(score_b-E_b))

    elo_df = elo_df.append(pd.Series(dtype=pd.Float64Dtype), ignore_index=True)

    for player in elo_df.columns:
        if player == player_a:
            elo_df[player].iloc[-1] = r_a
        elif player == player_b:
            elo_df[player].iloc[-1] = r_b
        else:
            elo_df[player].iloc[-1] = elo_df[player].values[-2]

    save_elo_df(elo_df)


def print_elos():
    elo_df = get_elo_df()
    pd.options.display.float_format = '{:.0f}'.format
    print(elo_df.iloc[-1].to_string())


def save_elo_df(elo_df):

    pickle.dump(elo_df, open('elo_df.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    drive.ListFile({'q': f"'{id}' in parents"}).GetList()[0].Delete()

    gfile = drive.CreateFile({'parents': [{'id': f'{id}'}]})
    gfile.SetContentFile('elo_df.pkl')
    gfile.Upload()
    time.sleep(0.5)


def get_elo_df():
    file_id = drive.ListFile({'q': f"'{id}' in parents and trashed=false"}).GetList()[0]['id']
    download_file = drive.CreateFile({'id': file_id})
    download_file.GetContentFile('elo_df.pkl')
    elo_df = pickle.load(open('elo_df.pkl', 'rb'))

    return elo_df


if __name__ == '__main__':
    reset_df()
    print_elos()
    #elo_update('Sam', 'Luca', 0, 1)
    #print_elos()


