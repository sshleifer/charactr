import matplotlib.pyplot as plt
from pylab import savefig
import seaborn as sns

pal = sns.color_palette("hls",6)
sns.set_style("white") 

def fig1(msg, fname): 
  '''Plot distribution of message length based on sent vs. received'''
  f, ax = plt.subplots(figsize=(7, 7))
  ax.set_xlim([0,100])
  got = msg[msg.is_sent == 0]
  sent = msg[msg.is_sent == 1]
  sns.kdeplot(got.msg_len, label="got",color=pal[0], shade=True,ax=ax,
      clip=(0,100))
  sns.kdeplot(sent.msg_len, label="sent", color=pal[4], shade=True, ax=ax,
      clip=(0,100))
  sns.despine()
  plt.xlabel('Message Length (chars)')
  savefig(fname)
  
def fig2(ppl, fname):
  '''For each contact, plot number of characters sent and received.'''
  sns.lmplot("lensent", "lenrec",ppl) 
  plt.xlabel('Characters Sent')
  plt.ylabel('Characters Received')
  sns.despine()
  savefig(fname)
