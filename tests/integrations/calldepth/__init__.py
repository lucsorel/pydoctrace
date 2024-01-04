def depth_6():
    return 6


def depth_5():
    return depth_6()


def depth_4():
    return depth_5()


def depth_3():
    return depth_4()


def depth_2():
    return depth_3()


def depth_1():
    return depth_2() + depth_4()
