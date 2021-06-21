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
    return results

def make_one_experiment(trace_dir, result_dir, prefetcher, n_warm, n_sim, log_path, case_num):
    #make experiment
    traces = os.listdir(trace_dir)
    num = 0
    for trace in traces:
        print("Start make experiment on {}...".format(trace))
        num += 1
        os.system("./run_champsim.sh {} {} {} {}".format(prefetcher, n_warm, n_sim, trace))
        if num > case_num:
            break
    #get result
    # results = get_experiment_result(result_dir)
    # f = open(log_path, "w+", encoding="utf-8")
    # for trace in results:
    #     f.write(trace + " : " + results[trace] + "\n")
    # f.close()


if __name__ == '__main__':
    trace_dir = "dpc3_traces"
    result_dir = "results_10M"
    #prefetcher = "bimodal-no-no-ip_stride-no-lru-1core"
    #ip_feature_prefetcher = "bimodal-no-ip_feature_find-no-no-lru-1core"
    #spp_prefetcher = "bimodal-no-next_line-next_line-no-lru-1core"
    #ipcp_prefetcher = "bimodal-no-ipcp-ipcp-ipcp-lru-1core"
    ip_value_finder = "bimodal-no-ip_page_change_frequency-no-no-lru-1core"


    branch_predicor = "bimodal"
    l1i_prefetcher = "no"
    l1d_prefetcher = "ip_page_change_frequency"
    l2c_prefetcher = "no"
    llc_prefetcher = "no"
    llc_replacement = "lru"
    core_num = "1"

    #compile
    os.system("./build_champsim.sh {} {} {} {} {} {} {}".format(branch_predicor, l1i_prefetcher, l1d_prefetcher, l2c_prefetcher, llc_prefetcher, llc_replacement, core_num))

    #ip_classifier_simple_prefetcher = "bimodal-no-ip_classifier_simple-ip_classifier_simple-no-lru-1core"
    #no_ip_classifier = "bimodal-no-no_ip_classifier-no_ip_classifier-no-lru-1core"
    make_one_experiment(trace_dir, result_dir, ip_value_finder, 1, 10, "{}".format(ip_value_finder), 1000)

