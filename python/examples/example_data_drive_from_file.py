# This example shows how to split a string into items that can be used to
# data drive a function. Examples include reading the data from a file and​
# parsing each line into individual pieces that can be used as input values​
# for a specific "transaction".​

#inputfile = '/apps/opt/software/numbers.txt'
inputfile = 'C:\\Users\\userid\\Documents\\numbers.txt'

# no file - just working with a CSV string into a list that will then be iterated.
def simpleslitstring():
    my_string = 'A,B,C,D,E'
    my_list = my_string.split(",")
    #print(my_list)
    for x in my_list[:]:
        doRealWork(x)

# example of a real function that would process 1 item from our list
def doRealWork(inputs):
    print("...place code for real work here ... current inputs are: " + str(inputs))

# from file - each line from the file is a "message" and the "message" can pass many "values". I am using ~ to delimit values in each message.
def splitfile():
    with open(inputfile) as f:
        lines = f.read().splitlines()
        for line in lines[:]:
            print(line)
            splitstring(line, "~")

def splitstring(line, delimiter):
    my_list = line.split(delimiter)
    print(my_list)

splitfile()

print("")
print("...case 2... show how to drive the doRealWork function")
simpleslitstring()

