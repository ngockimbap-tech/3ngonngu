#number of test cases
t = int(input())

#input t test cases
for i in range (t):
    i = int(input()) #number of elements
    j = list(map(int, input().split())) #input list of elements
    c_1 = 0 #cout number of 1
    c_0 = 0 #cout number of 0
    
    #in Bessie turn, she will create an 1 and detete an 0 
    #in Elsie turn, she will create an 0 and detete an 1
    for k in range(i):
        if j[k] == 1:
            c_1 += 1
        else:
            c_0 += 1
    
    #if numbers of 1 > numbers of 0 => Bessie has more chance to create more 1 => Bessie win
    #if numbers of 1 < numbers of 0 => Bessie has more chance to create more 0 => Elsie win
    #if numbers of 1 = numbers of 0 => they have the same chance but Bessie go first => Bessie win
    if c_1 >= c_0:  
        print("Bessie")
    else:
        print("Elsie")
