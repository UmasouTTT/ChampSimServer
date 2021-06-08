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



def read_ip_value(path):
    ip_value = {}
    f = open(path, "r+", encoding="utf-8")
    for line in f:
        content = line.strip().split(":")
        ip = content[1].replace(" ","").replace("value", "")
        value = round(float(content[2].replace("appear ", "")), 2)
        appear = int(content[3].replace(" ", "").replace("hit", ""))
        ip_value[ip] = [value, appear]
    f.close()
    return ip_value

def deal_with_ip(ip_value):
    valuable_ips = []
    for ip in ip_value:
        if ip_value[ip][0] >= 0.8:
            valuable_ips.append(ip)
        # if ip_value[ip][1] >= 1000:
        #     valuable_ips.append(ip)
        else:
            print("valuless ip : {}".format(ip_value[ip]))
    print("important ip num : {}, percentage : {}".format(len(valuable_ips), len(valuable_ips)/len(ip_value)))
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
        percentage = deal_with_ip(read_ip_value("log.txt"))
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
    valuable_ips = deal_with_ip(read_ip_value("ip_value_log.txt"))
    reload_valuable_ips(valuable_ips, important_ip_file)




if __name__ == '__main__':
    trace = ""
    trace_dir = "dpc3_traces"
    result_dir = "results_10M"
    important_ip_file = "important_ips.txt"
    n_warm = 50
    n_sim = 200
    ip_valuable_analysisor = "bimodal-no-ipcp_ip_value-ipcp-ipcp-lru-1core"
    prefetcher = "bimodal-no-ip_classifier_v2_value_ip-ip_classifier_v1-no-lru-1core"
    #prefetcher = "bimodal-no-classifier_v3_only_classify-no-no-lru-1core"



    #make experiment
    traces = os.listdir(trace_dir)
    for trace in traces:
        print("Start make experiment on {}".format(trace))
        print("Start find valuable ips ...")
        #bimodal-no-ipcp_ip_value-ipcp-ipcp-lru-1core
        find_important_ip(trace, ip_valuable_analysisor, n_warm, n_sim, important_ip_file)
        #print("Start make experiment ...")
        os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))


