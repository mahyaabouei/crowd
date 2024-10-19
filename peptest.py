import datetime
from persiantools.jdatetime import JalaliDate

ppp = str(JalaliDate(datetime.datetime.now())).replace('-', '/')
print(ppp)