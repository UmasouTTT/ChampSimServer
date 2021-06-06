import os
from py_tool.common import reverse_sort_dict_by_value_return_list





def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def get_experiment_result(path):
    traces_results_path = get_files(path)
    results = {}
    for path in traces_results_path:
        if "ip_feature_find" in path:
            continue
        trace_name = path.split("/")[-1].split('-')[0]
        f = open(path, "r+", encoding="utf-8")
        for line in f:
            if "CPU 0 cumulative IPC:" in line:
                ipc = line.split(" ")[4]
                results[trace_name] = ipc
                break
        f.close()
        #os.remove(path)
    return results



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
    valuable_ips = []
    percentage = 0
    for ip in sorted_ip:
        valuable_ips.append(ip[0])
        percentage += ip_frequency[ip[0]] / sum(ip_frequency.values())
        if percentage > 0.9:
            break
    print("important ip num : {}, whole ip num : {}, percentage : {}".format(len(valuable_ips), len(ip_frequency),percentage))
    return valuable_ips

def reload_valuable_ips(valuable_ips, reload_path):
    f = open(reload_path, "w+", encoding="utf-8")
    for ip in valuable_ips:
        f.write(ip + "\n")
    f.close()

def make_one_experiment(trace_dir, prefetcher, n_warm, n_sim, log_path, case_num):
    #make experiment
    traces = os.listdir(trace_dir)
    num = 0
    for trace in traces:
        num += 1
        os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
        if num > case_num:
            break
        #observation
        percentage = deal_with_ip(read_ip_frequency("log.txt"))
        print(trace.split('.')[1].split('-')[0], percentage)

def make_experiment_by_ip_frequency(trace_dir, prefetcher, n_warm, n_sim, log_path, important_ip_file):
    #make experiment
    traces = os.listdir(trace_dir)
    for trace in traces:
        find_important_ip(trace, ip_feature_prefetcher, n_warm, n_sim, important_ip_file)
        os.system("./run_champsim.sh {} {} {} {}".format(ip_classifier_prefetcher, n_warm, n_sim, trace))
    #get result
    results = get_experiment_result(result_dir)
    f = open(log_path, "w+", encoding="utf-8")
    for trace in results:
        f.write(trace + " : " + results[trace] + "\n")
    f.close()

def find_important_ip(trace, prefetcher, n_warm, n_sim, relod_path):
    os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
    valuable_ips = deal_with_ip(read_ip_frequency("log.txt"))
    return valuable_ips
    #reload_valuable_ips(valuable_ips, relod_path)
    #os.remove(important_ip_file)



if __name__ == '__main__':
    trace_dir = "dpc3_traces"
    result_dir = "results_10M"
    important_ip_file = "important_ips.txt"
    n_warm = 1
    n_sim = 10
    #prefetcher = "bimodal-no-no-ip_stride-no-lru-1core"
    ip_feature_prefetcher = "bimodal-no-ip_feature_find-no-no-lru-1core"
    #spp_prefetcher = "bimodal-no-next_line-next_line-no-lru-1core"
    #make_one_experiment(trace_dir, ip_feature_prefetcher, 1, 10, "{}".format(ip_feature_prefetcher), 100)

    ip_classifier_prefetcher = "bimodal-no-ip_classifier_v1-ip_classifier_v1-no-lru-1core"
    # ips = find_important_ip("602.gcc_s-734B.champsimtrace.xz", ip_feature_prefetcher, n_warm, n_sim, important_ip_file)
    # reload_valuable_ips(ips, important_ip_file)
    # os.system("./run_champsim.sh {} {} {} {}".format(ip_classifier_prefetcher, n_warm, n_sim, "602.gcc_s-734B.champsimtrace.xz"))


    prefetcher = ip_classifier_prefetcher

    # #make experiment
    traces = os.listdir(trace_dir)
    for trace in traces:
        print("Start make experiment on {}".format(trace))
        print("Start find valuable ips ...")
        #os.system("./run_champsim.sh {} {} {} {}".format(ip_feature_prefetcher, n_warm, n_sim, trace))
        ips = find_important_ip(trace, ip_feature_prefetcher, n_warm, n_sim, important_ip_file)
        reload_valuable_ips(ips, important_ip_file)
        print("Start make experiment ...")
        os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
    #get result
    print("Start deal with results")
    results = get_experiment_result(result_dir)
    f = open("{}".format(prefetcher), "w+", encoding="utf-8")
    for trace in results:
        f.write(trace + " : " + results[trace] + "\n")
    f.close()

