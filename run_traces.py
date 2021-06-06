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
    results = get_experiment_result(result_dir)
    f = open(log_path, "w+", encoding="utf-8")
    for trace in results:
        f.write(trace + " : " + results[trace] + "\n")
    f.close()


if __name__ == '__main__':
    trace_dir = "dpc3_traces"
    result_dir = "results_10M"
    #prefetcher = "bimodal-no-no-ip_stride-no-lru-1core"
    #ip_feature_prefetcher = "bimodal-no-ip_feature_find-no-no-lru-1core"
    #spp_prefetcher = "bimodal-no-next_line-next_line-no-lru-1core"
    #ipcp_prefetcher = "bimodal-no-ipcp-ipcp-ipcp-lru-1core"
    #ip_classifier_simple_prefetcher = "bimodal-no-ip_classifier_simple-ip_classifier_simple-no-lru-1core"
    no_ip_classifier = "bimodal-no-no_ip_classifier-no_ip_classifier-no-lru-1core"
    make_one_experiment(trace_dir, result_dir, no_ip_classifier, 1, 10, "{}".format(no_ip_classifier), 100)

