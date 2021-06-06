import os
def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def get_experiment_result(path):
    traces_results_path = get_files(path)
    results = {}
    for path in traces_results_path:
        trace_name = path.split('/')[-1].split(".champ")[0]
        f = open(path, "r+", encoding="utf-8")
        for line in f:
            if "CPU 0 cumulative IPC:" in line:
                ipc = line.split(" ")[4]
                results[trace_name] = ipc
                break
        f.close()
    return results


results_dir = "results"
log_path = "prefetcher_results/ipcp"
#get result
results = get_experiment_result(results_dir)
f = open(log_path, "w+", encoding="utf-8")
for trace in results:
    f.write(trace + " : " + results[trace] + "\n")
f.close()