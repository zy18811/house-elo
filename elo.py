import pandas as pd
import pickle


def reset_df(starting_elo=1000):
    elo_df = pd.DataFrame(columns=['Sam','Luca','Amy','Gabriel'])
    elo_df.loc[0] = starting_elo
    pickle.dump(elo_df, open('elo_df.pkl', 'wb'),protocol=pickle.HIGHEST_PROTOCOL)


def add_player(name):
    elo_df = pickle.load(open('elo_df.pkl','rb'))
    elo_df[name] = 1000
    pickle.dump(elo_df, open('elo_df.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


def elo_update(player_a, player_b, score_a, score_b):
    k = 32  # what USCF uses for <2100

    elo_df = pickle.load(open('elo_df.pkl','rb'))
    r_a = elo_df[player_a].iloc[-1]
    r_b = elo_df[player_b].iloc[-1]

    Q_a = 10**(r_a/400)
    Q_b = 10**(r_b/400)

    E_a = Q_a/(Q_a+Q_b)
    E_b = Q_b/(Q_a+Q_b)

    r_a += int(k*(score_a-E_a))
    r_b += int(k*(score_b-E_b))

    elo_df = elo_df.append(pd.Series(dtype=float), ignore_index=True)

    for player in elo_df.columns:
        if player == player_a:
            elo_df[player].iloc[-1] = r_a
        elif player == player_b:
            elo_df[player].iloc[-1] = r_b
        else:
            elo_df[player].iloc[-1] = elo_df[player].iloc[-2]
    pickle.dump(elo_df, open('elo_df.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

reset_df()
