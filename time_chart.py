#
#   A new figure dealing with time
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# accepts msg dataframe (return val of chat_to_csv.writeChat())
# returns dataframe of texts by time
def timeDf(msg):
    msg["hour"] = msg.date.apply(lambda x : int(x[-8:-6]))
    msg_groups = msg.groupby("hour")

    tot = msg_groups.is_sent.size()
    # first column automatically named 0 for some reason
    df = pd.DataFrame(tot)
    df = df.rename(columns={0 : 'tot'})
    df["snt"] = msg_groups.is_sent.agg(sum)
    df["rec"] = df.tot - df.snt

    # uncomment to automatically show plots
    # df.plot()
    # plt.show()
    return df
