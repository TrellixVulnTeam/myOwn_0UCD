import calendar

year = int(input("Enter audit year: "))

file = open('auditYear.txt', 'w')
file.write("Audit year: " + str(year) + "\n")

for month in range(1, 13):

    mycal = calendar.monthcalendar(year, month)
    #print(mycal)
    
    for week in range(0, len(mycal)):

        week_day = mycal[week]
        
        if week_day[calendar.THURSDAY] != 0:
            
            audit_day = week_day[calendar.THURSDAY]
            file.write("weekly MT %3s %2d" % (calendar.month_name[month], audit_day) + "\n")
            print("weekly MT %3s %2d" % (calendar.month_name[month], audit_day))

        if week == (len(mycal)-1):
            #print(len(mycal)-1)
            for day in week_day:
                #print(day)
                #last_day = day
                
                if (day == 28
                    and (day != week_day[calendar.FRIDAY]
                    or day != week_day[calendar.SATURDAY])
                    and month == 2):
                    last_day = day
                    continue                
                elif (day == 29
                    and (day != week_day[calendar.FRIDAY]
                    or day != week_day[calendar.SATURDAY])
                    and month == 2):
                    last_day = day
                    break
                
                if (day == 30
                    and (day != week_day[calendar.FRIDAY]
                    or day != week_day[calendar.SATURDAY])):                
                    last_day = day
                    continue                
                elif (day == 31
                    and (day != week_day[calendar.FRIDAY]
                    or day != week_day[calendar.SATURDAY])):
                    last_day = day
                    break
                elif 1 <= day < 30:
                    last_day = audit_day
                    continue

            file.write("monthly MT %3s %2d" % (calendar.month_name[month], last_day) + "\n")    
            print("monthly MT %3s %2d" % (calendar.month_name[month], last_day))

file.close()
        
