# BUBBLE SORT
def bubble_sort(lst):
    arr = lst.copy()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# SELECTION SORT
def selection_sort(lst):
    arr = lst.copy()
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

#INSERTION SORT
def insertion_sort(lst):
    arr = lst.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

#MERGE SORT
def merge_sort(lst):
    # Base case: a list of 0 or 1 elements is already sorted
    if len(lst) <= 1:
        return lst.copy()
        
    mid = len(lst) // 2
    left = merge_sort(lst[:mid])
    right = merge_sort(lst[mid:])
    
    # Merge helper logic to combine the sorted halves
    sorted_arr = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            sorted_arr.append(left[i])
            i += 1
        else:
            sorted_arr.append(right[j])
            j += 1
            
    sorted_arr.extend(left[i:])
    sorted_arr.extend(right[j:])
    return sorted_arr

#HEAP SORT
def heap_sort(lst):
    arr = lst.copy()
    n = len(arr)

    def heapify(length, root_idx):
        largest = root_idx
        left = 2 * root_idx + 1
        right = 2 * root_idx + 2

        if left < length and arr[left] > arr[largest]:
            largest = left
        if right < length and arr[right] > arr[largest]:
            largest = right

        if largest != root_idx:
            arr[root_idx], arr[largest] = arr[largest], arr[root_idx]
            heapify(length, largest)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(i, 0)
        
    return arr

#QUICK SORT
def quick_sort(lst):
    if len(lst) <= 1:
        return lst.copy()
        
    # Using the middle element as a stable pivot point
    pivot = lst[len(lst) // 2]
    
    left = [x for x in lst if x < pivot]
    middle = [x for x in lst if x == pivot]
    right = [x for x in lst if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

if __name__ == "__main__":
    arr = [7,4,9,1,5]

    print(bubble_sort(arr))
    print(selection_sort(arr))
    print(insertion_sort(arr))
    print(merge_sort(arr))
    print(heap_sort(arr))
    print(quick_sort(arr))