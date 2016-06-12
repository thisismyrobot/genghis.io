# Explore randomly
# Moving the Sphero around randomly to explore the environment
"""
    Explore randomly
"""
import random


@behaviour(priority=1)
def drive_square():
    direction = random.choice(['forwards', 'right', 'backwards', 'left'])
    speed = random.randint(32, 255)
    
    if direction == 'forwards':
        robot.move_forwards(speed)
    elif direction == 'right':
        robot.move_right(speed)
    elif direction == 'backwards':
        robot.move_backwards(speed)
    elif direction == 'left':
        robot.move_left(speed)

    robot.stop()
