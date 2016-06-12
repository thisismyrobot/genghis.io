# Counter
# An example of counting using the memory store
"""
    A basic counter
"""
@behaviour(priority=1)
def counter():
    # Load the counter from memory, set it to zero if first time
    counter_value = memory.load('counter', 0)

    # Print out the value of the counter
    debug(counter_value)

    # Increment the counter by 1
    counter_value = counter_value + 1

    # Save it back in the memory
    memory.save('counter', counter_value)
