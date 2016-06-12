# Drive in a Square
# Moving the Sphero around in a square pattern
"""
    Drive in a square
"""
@behaviour(priority=1)
def drive_square():
    debug('Mmmmm, squares...')
    robot.move_forwards(64)
    wait(2)
    robot.stop()
    wait(1)
    robot.move_right(64)
    wait(2)
    robot.stop()
    wait(1)
    robot.move_backwards(64)
    wait(2)
    robot.stop()
    wait(1)
    robot.move_left(64)
    wait(2)
    robot.stop()
    wait(5)
