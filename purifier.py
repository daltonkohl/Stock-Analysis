f = open("stock_data.txt", "r")



#dirty data purifier
new_f  = open("trainingnewclean.txt", "a")
for line in f:
    if len(line.split(",")) > 25 or len(line.split(",")) < 25:
        pass
    else:
        line_split = line.split(",")
        valid_line = True
        try:
            for i in range(len(line_split)):
                float_try = float(line_split[i])
                if line_split[i] == " " or line_split[i] == "":
                    valid_line = False
            line = ""
            for num in line_split:
                line += num + ","
            line = line[:-1]
            if line[0].isnumeric() and valid_line:
                print("write")
                new_f.write(line)
        except:
            print("nice try dirty data")

new_f.close()