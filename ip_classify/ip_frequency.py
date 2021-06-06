import os
from py_tool.common import reverse_sort_dict_by_value_return_list

def read_ip_frequency(path):
    ip_frequency = {}
    f = open(path, "r+", encoding="utf-8")
    for line in f:
        count = line.strip().split(":")[-1]
        ip = line.strip().split(" ")[1]
        ip_frequency[ip] = int(count)
    f.close()
    os.remove(path)
    return ip_frequency

def deal_with_ip(ip_frequency):
    sorted_ip = reverse_sort_dict_by_value_return_list(ip_frequency)
    percentage = 0
    num = 0
    result = ""
    for ip in sorted_ip:
        result += ip[0]
        num += 1
        percentage += ip_frequency[ip[0]] / sum(ip_frequency.values())
        if percentage > 0.8:
            break
        result += ","
    print(num, len(ip_frequency))


import os

def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def get_experiment_result(path):
    traces_results_path = get_files(path)
    results = {}
    for path in traces_results_path:
        trace_name = path.split("/")[-1].split('-')[0]
        f = open(path, "r+", encoding="utf-8")
        for line in f:
            if "CPU 0 cumulative IPC:" in line:
                ipc = line.split(" ")[4]
                results[trace_name] = ipc
                break
        f.close()
        os.remove(path)
    return results

def make_one_experiment(trace_dir, result_dir, prefetcher, n_warm, n_sim, log_path, case_num):
    #make experiment
    traces = os.listdir(trace_dir)
    num = 0
    for trace in traces:
        num += 1
        os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
        if num > case_num:
            break
    #get result
    results = get_experiment_result(result_dir)
    f = open(log_path, "w+", encoding="utf-8")
    for trace in results:
        f.write(trace + " : " + results[trace] + "\n")
    f.close()

    #observation
    deal_with_ip(read_ip_frequency(os.path.abspath('..') + "/log.txt"))


if __name__ == '__main__':
    trace_dir = os.path.abspath('..') + "/dpc3_traces"
    result_dir = os.path.abspath('..') + "/results_10M"
    #prefetcher = "bimodal-no-no-ip_stride-no-lru-1core"
    ip_feature_prefetcher = "bimodal-no-ip_feature_find-no-no-lru-1core"
    #spp_prefetcher = "bimodal-no-next_line-next_line-no-lru-1core"
    make_one_experiment(trace_dir, result_dir, ip_feature_prefetcher, 1, 10, "{}".format(ip_feature_prefetcher), 1)



