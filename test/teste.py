import calendar
import time

currentGmt = time.gmtime()
inital_timestamp = calendar.timegm(currentGmt)

currentGmt = time.gmtime()
end_timestamp = calendar.timegm(currentGmt)


tuplas = [("a", "b")]
print(tuplas[0][0])