from dateutil.parser import parse
import datetime

text = "Thu Feb 13 2020 20:55:40 GMT+0600"
processed_text = text[0:16]
dt = parse(processed_text)
print(dt)
# datetime.datetime(2010, 2, 15, 0, 0)
print(dt.strftime('%d/%m/%Y'))
# 15/02/2010

# using datetime
p = "Thu Feb 13 2020 20:55:40 GMT+0600"
l = p[0:15]
print(l)
dt = datetime.datetime.strptime(l, '%a %b %d %Y').strftime('%d/%m/%Y')
print(dt)
# datetime.datetime(2010, 2, 15, 0, 0)
# print(dt.strftime('%d/%m/%Y'))
# 15/02/2010
