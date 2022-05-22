count = 0

def myfunction(addin):
    global count
    count = count + addin
    print("inside.myfunction.count=" + str(count))

print("outside.main.checkpoint0.count=" + str(count))
myfunction(1)
print("outside.main.checkpoint1.count=" + str(count))
myfunction(6)
print("outside.main.checkpoint2.count=" + str(count))
