from itertools import cycle

# Example list
my_list = [1, 2, 3, 4, 5]

# Create a cycle iterator from the list
circular_iterator = cycle(my_list)

# Iterate through the list indefinitely
for _ in range(5):  # You can specify any number of iterations or use a while loop for indefinite iteration
    next_element = next(circular_iterator)
    print(next_element, my_list)
    my_list.pop(0)