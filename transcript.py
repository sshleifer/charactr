execfile('t.py')

def formPrint(row, last):
    if (row['date_orig'] - last['date_orig']) > 3599:
        print
        print '     ', row['date']

    if row['is_sent'] == 0:
        print row['text']
    else:
        print '                ', row['text']

sam = work[work.cname == 'sam shleifer ']
hai = pd.DataFrame(sam.text, columns = ['text'])
hai['date'] = sam.date
hai['date_orig'] = sam.date_orig
hai['is_sent'] = sam.is_sent

row_iterator = hai.iterrows()
_, last = row_iterator.next()

print '     ', last['date']
formPrint(last, last)
for index, row in row_iterator:
    formPrint(row, last)
    last = row
