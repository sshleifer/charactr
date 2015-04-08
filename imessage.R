require(dplyr)
require(ggplot2)
require(lubridate)
#TODO (ODBC)
msg = read.csv('msg.csv') # My local copy. Needs fix

msg = mutate(msg, 
             text = as.character(text),
             ml = nchar(text), 
             date = ymd("2001-01-01") + seconds(msg$date),
             io = ifelse(is_sent==1, 'Sent','Got'))


ggplot(msg, aes(x=ml, fill=io))+geom_density(alpha=.7) +
  scale_x_log10() +
  facet_wrap(~handle_id)


ppl = group_by(msg,handle_id) %>% 
  summarise(msent = mean(is_sent), n=length(is_sent), lensent = sum(is_sent*ml), totlen = sum(ml))%>%
  mutate(lenrec =  totlen-lensent) %>% filter(handle_id != 0)
                                             
ggplot(ppl, aes(x=lensent, y=lenrec, size=n)) +
  geom_smooth() + 
  geom_point() +
  theme_bw()
