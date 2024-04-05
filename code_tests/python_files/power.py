target = 2
pov = 10
if pov == 0:
    target = 1
else:
    intermediary = 1
    while pov > 0:
        val = pov % 2
        if val == 0:
            number_of_muls = pov // 2
            pov = pov - number_of_muls
            while number_of_muls > 0:
                intermediary = intermediary * target
                number_of_muls = number_of_muls - 1
        else:
            intermediary = intermediary * target
            pov = pov - 1
    target = intermediary
