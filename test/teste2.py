def reorganize_list(lst, N):
    return lst[N:] + lst[:N]

# Example usage:
original_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
N = 0  # N is the position until where you want to move the elements to the end
reorganized_list = reorganize_list(original_list, N)
print(reorganized_list)
