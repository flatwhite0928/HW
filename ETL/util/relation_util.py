from queue import Queue
import copy


def fetch(input_data, relation):
    """

    :param input_data:
    :param relation:
    :return:
    """
    resolved_path = relation.split(".")

    queue = Queue()
    queue.put(input_data)

    path_count = 0

    list_count = 0
    list_divide = []
    list_divide_num = []
    # this list is to store the nested data information
    index_list = []

    result_list = []

    last_list_idx = 0

    for path in resolved_path:
        if path == "list":
            list_divide.append([])
            last_list_idx += 1

    while len(queue.queue) != 0:
        size = len(queue.queue)
        current_path = resolved_path[path_count]

        # size means in each level, how many objects are they
        for i in range(size):
            tmp_data = queue.get()
            if current_path == "list":
                for data in tmp_data:
                    queue.put(data)

                # to make nested structure
                if len(list_divide[list_count]) >= 1:
                    length = len(tmp_data) + list_divide[list_count][-1]
                else:
                    length = len(tmp_data)
                list_divide[list_count].append(length)

                # find the path to the target folder, at the end of calculation, we build the nest structure
                if list_count == last_list_idx - 1:
                    idxes = []
                    for i in range(list_count, -1, -1):
                        if i == list_count:
                            idxes.append(len(list_divide[i]) - 1)
                        else:
                            for j in range(len(list_divide[i])):
                                if list_divide[i][j] >= len(list_divide[i + 1]):
                                    idxes.append(j)
                                    break

                    idxes.reverse()
                    index_list.append(idxes)

                    list_divide_num = copy.deepcopy(list_divide)

                    for i in range(len(list_divide)):
                        for j in range(len(list_divide[i]) - 1, 0, -1):
                            list_divide_num[i][j] = list_divide_num[i][j] - list_divide_num[i][j - 1]
            else:
                if path_count < len(resolved_path) - 1:
                    queue.put(tmp_data[current_path])
                else:
                    result_list.append(tmp_data[current_path])
        # show
        if current_path == "list":
            list_count += 1
        path_count += 1

    put_queue = Queue()

    # reconstruct the nested list
    for i in range(last_list_idx - 1, -1, -1):
        tmp_size = list_divide[i]
        tmp_set = set()
        for j in range(len(index_list)):
            tmp_set.add(index_list[j][i])
        if i == last_list_idx - 1:
            for z in range(len(tmp_set)):
                if z == 0:
                    start_point = 0
                else:
                    start_point = tmp_size[z - 1]
                end_point = tmp_size[z]
                put_queue.put(result_list[start_point:end_point])
        else:
            for z in range(len(tmp_set)):
                put_list = []
                tmp_size = list_divide_num[i]
                for x in range(tmp_size[z]):
                    put_list.append(put_queue.get())
                put_queue.put(put_list)

    if "list" not in relation:
        return result_list[0]
    else:
        return put_queue.get()