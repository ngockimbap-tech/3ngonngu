sdk_num = int(input())
for i in range (sdk_num):
    sdk = []
    for j in range (9):
        sdk.append(input())
        
    rows = []
    for k in range (9):
        rows.append([])
    
    cols = []
    for m in range (9):
        cols.append([])
        
    boxes = []
    for n in range (9):
        boxes.append([])
    
    for r in range (9):
        for c in range (9):
            ele = sdk[r][c]
            if ele != ".":
                rows[r].append(ele)
                cols[c].append(ele)
                b = (r//3)*3 + c//3
                boxes[b].append(ele)
    
    val = True
    
    for i in range (9):
        if len(rows[i]) != len(set(rows[i])):
            val = False
            break
        if len(cols[i]) != len(set(cols[i])):
            val = False
            break
        if len(boxes[i]) != len(set(boxes[i])):
            val = False
            break
    
    if val:
        print("VALID")
    else:
        print("INVALID")
