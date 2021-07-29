def findNextCellToFill(grid, i, j):
        for x in range(i,9):
                for y in range(j,9):
                        if grid[x][y] == 0:
                                return x,y
        for x in range(0,9):
                for y in range(0,9):
                        if grid[x][y] == 0:
                                return x,y
        return -1,-1

def isValid(grid, i, j, e):
        rowOk = all([e != grid[i][x] for x in range(9)])
        if rowOk:
                columnOk = all([e != grid[x][j] for x in range(9)])
                if columnOk:
                        # finding the top left x,y co-ordinates of the section containing the i,j cell
                        secTopX, secTopY = 3 *(i//3), 3 *(j//3) #floored quotient should be used here. 
                        for x in range(secTopX, secTopX+3):
                                for y in range(secTopY, secTopY+3):
                                        if grid[x][y] == e:
                                                return False
                        return True
        return False

def solveSudoku(grid, i=0, j=0):
        i,j = findNextCellToFill(grid, i, j)
        if i == -1:
                return True
        for e in range(1,10):
                if isValid(grid,i,j,e):
                        grid[i][j] = e
                        if solveSudoku(grid, i, j):
                                return True
                        # Undo the current cell for backtracking
                        grid[i][j] = 0
        return False

def sudoku_list_to_string(l):
    foo = ""
    for i in l:
        for j in i:
            if j == 0:
                foo += '.'
            else:
                foo += str(j)
    
    return foo

def try_int(x):
    try:
        return int(x)
    except ValueError:
        return 0

def sudoku_string_to_list(m):
    previous = 0
    main_list = []

    for i in range(9,82,9):
        main_list.append([try_int(h) for h in m[previous:i]])
        previous = i
    
    return main_list

#this code shit do be hzrd doe... like me when i see brian 
def solveWrapper(x):
    input = [i for i in x]
    solveSudoku(input)
    return input