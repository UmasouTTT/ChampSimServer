def sort_dict_by_value_return_list(dict):
    result = sorted(dict.items(), key=lambda x:[x[1], x[0]])
    result = [list(item) for item in result]
    return result

def reverse_sort_dict_by_value_return_list(dict):
    result = sorted(dict.items(), key=lambda x:[x[1], x[0]], reverse=True)
    result = [list(item) for item in result]
    return result