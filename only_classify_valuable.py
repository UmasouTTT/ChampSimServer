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
    whole_num = 0
    whole_prefetch_num = 0
    valuable_ip_num = 0
    whole_value = 0

    for line in f:
        content = line.strip().split("|")
        ip = content[0].split(":")[-1]
        value = round(float(content[1].split(":")[-1]), 2)
        if value > 0:
            valuable_ip_num += 1
            whole_value += value
        prefetch_num = int(content[2].split(":")[-1])
        hit = int(content[3].split(":")[-1])
        ip_frequency = int(content[4].split(":")[-1])
        whole_num += ip_frequency
        whole_prefetch_num += prefetch_num
        ip_value[ip] = [value, ip_frequency, prefetch_num, hit, whole_prefetch_num]
    f.close()

    result = sorted(ip_value.items(), key=lambda x: x[1][0], reverse=True)

    for ip in result:
        ip[1][4] = ip[1][2] / whole_prefetch_num
        print("ip:{}, accuracy:{}, percentage:{}, frequency:{}, prefetch_num:{}".format(ip[0], ip[1][0], round(ip[1][1]/whole_num, 2),
                                                                                        ip[1][1], ip[1][2]))
    occupy = 0
    valuless_ips = []
    valuable_ips = []
    avg_value = whole_value / valuable_ip_num
    print("avg_value:", avg_value)
    start_less_valuable = False
    for ip in result:
        if ip[1][0] >= 0.5 * avg_value:
            valuable_ips.append(ip[0].strip())
        if ip[1][0] > 0:
            valuless_ips.append(ip[0].strip())


        # occupy += ip[1][4]
        # if ip[1][0] <= 0.001:
        #     break
        # if ip[1][0] <= 0.3:
        #     start_less_valuable = True



    print("valuable_ips:{}".format(valuable_ips))
    print("valuless_ips:{}".format(valuless_ips))
    return valuable_ips, valuless_ips

def deal_with_ip(ip_value):
    valuable_ips = []
    for ip in ip_value:
        if ip_value[ip][0] > 0:
            valuable_ips.append(ip)
        # if ip_value[ip][1] >= 1000:
        #     valuable_ips.append(ip)
        else:
            print("valuless ip : {}".format(ip_value[ip]))
    print("important ip num : {}, percentage : {}".format(len(valuable_ips), len(valuable_ips)/len(ip_value)))
    return valuable_ips

def reload_valuable_ips(valuable_ips, valuless, reload_valuable_path, reload_valuless_path):
    f = open(reload_valuable_path, "w+", encoding="utf-8")
    for ip in valuable_ips:
        f.write(ip + "\n")
    f.close()

    f = open(reload_valuless_path, "w+", encoding="utf-8")
    for ip in valuless:
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

def find_important_ip(trace, prefetcher, n_warm, n_sim, relod_valuable_path, relod_valuless_path):
    os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
    valuable_ips, valuless = read_ip_value("ip_value_l1.txt")

    # print("l1 condition:")
    # valuable_ips_l1 = read_ip_value("ip_value_l1.txt")
    # print("l2 condition:")
    # valuable_ips_l2 = read_ip_value("ip_value_l2.txt")
    # valubale_ips = set()
    # all_ips = set()
    #
    # for ip in valuable_ips_l1:
    #     all_ips.add(ip)
    #     if valuable_ips_l1[ip][0] > 0:
    #         valubale_ips.add(ip)
    #
    # for ip in valuable_ips_l2:
    #     all_ips.add(ip)
    #     if valuable_ips_l2[ip][0] > 0:
    #         valubale_ips.add(ip)
    #
    # print("valuable ip percentage:{}".format(len(valubale_ips) / len(all_ips)))
    reload_valuable_ips(valuable_ips, valuless, relod_valuable_path, relod_valuless_path)

def compile_prefetcher(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num):
    os.system("./build_champsim.sh {} {} {} {} {} {} {}".format(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num))

if __name__ == '__main__':
    trace = ""
    trace_dir = "dpc3_traces"
    result_dir = "results_10M"
    valuable_fir = "important_ips.txt"
    valuelss_fir = "valuless_ips.txt"
    n_warm = 1
    n_sim = 10
    ip_valuable_analysisor = "bimodal-no-paper_ipcp_value-paper_ipcp_value-no-lru-1core"
    #prefetcher = "bimodal-no-ip_classifier_v2_value_ip-ip_classifier_v1-no-lru-1core"
    #prefetcher = "bimodal-no-classifier_v3_only_classify-no-no-lru-1core"
    ip_classify_paper = "bimodal-no-ipcp_only_important-ipcp_only_important-no-lru-1core"
    #ip_classify_paper_compare = "bimodal-no-paper_ipcp_ip_classify_v1-paper_ipcp-no-lru-1core"

    #build
    branch_predicor = "bimodal"
    l1i_prefetcher = "no"
    l1d_prefetcher = "paper_ipcp_value"
    l2c_prefetcher = "paper_ipcp_value"
    llc_prefetcher = "no"
    llc_replacement = "lru"
    core_num = "1"

    #compile
    print("Start compile {} {} {} {} {} {} {}...".format(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num))
    compile_prefetcher(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num)

    l1d_prefetcher = "ipcp_only_important"
    l2c_prefetcher = "ipcp_only_important"
    compile_prefetcher(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num)



    #make experiment
    traces = os.listdir(trace_dir)
    for trace in traces:
        print("Start make experiment on {}".format(trace))
        print("Start find valuable ips ...")
        #bimodal-no-ipcp_ip_value-ipcp-ipcp-lru-1core
        find_important_ip(trace, ip_valuable_analysisor, n_warm, n_sim, valuable_fir, valuelss_fir)
        #print("Start make experiment ...")
        os.system("./run_champsim.sh {} {} {} {}".format(ip_classify_paper, n_warm, n_sim, trace))
        #find valuless-pattern
        # f = open("valuess_pattern.txt", "r+", encoding="utf-8")
        # valuless_pattern = f.readlines()
        # f.close()
        # f = open("valuless:{}".format(trace), "w+", encoding="utf-8")
        # for line in valuless_pattern:
        #     f.write(line)
        # f.close()

