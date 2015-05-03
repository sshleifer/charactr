#
#   New figures dealing with time and date
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# accepts msg dataframe (return val of chat_to_csv.writeChat())
# returns dataframe of texts by time and dataframe of texts by month
def timeDf(msg):

    ######################## time of day #########################

    msg["hour"] = msg.date.apply(lambda x : int(x[-8:-6]))
    msg_groups = msg.groupby("hour")

    tot = msg_groups.is_sent.size()
    # first column automatically named 0 for some reason
    time_df = pd.DataFrame(tot)
    time_df = time_df.rename(columns={0 : 'tot'})
    time_df["snt"] = msg_groups.is_sent.agg(sum)
    time_df["rec"] = time_df.tot - time_df.snt

    # time_df.plot()
    # plt.show()


    ########################### date #############################

    msg['yr'] = msg.date.apply(lambda x : int(x[:4]))
    msg['mo'] = msg.date.apply(lambda x : int(x[5:7]))
    min_yr = msg.yr.min()
    min_mo = msg.loc[msg['yr'] == min_yr].mo.min()

    mo_gr = msg.groupby('mo')
    yr_gr = mo_gr.apply(lambda x : x.groupby('yr'))
    tot = yr_gr.apply(lambda x : x.is_sent.size())

    date_df = pd.DataFrame(tot.unstack())
    # haven't been able to get snt/rec
        # thought yr_gr.apply(lambda x : x.is_sent.agg(sum)) would work

    # date_df.plot()
    # plt.show()
    return time_df, date_df
