x = 0
y = 0
if x == 0:
    x = 1
    if y == 0:
        y = 2

    x *= 2
    if x > y:
        y *= x
    elif x < y:
        x *= y
