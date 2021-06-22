import os
import matplotlib.pyplot as plt
import numpy as np

def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def getContentsFromTargetPrefetcher(results):
    results = get_files(results)
    prefetcher_ipc = {}
    traces = set()
    for result in results:
        if "DS_Store" in result:
            continue
        f = open(result, "r+", encoding="utf-8")
        trace = result.split('/')[-1].split(".champ")[0]
        traces.add(trace)
        for line in f:
            if "CPU 0 cumulative IPC:" in line:
                ipc = line.split(" ")[4]
                prefetcher_ipc[trace] = round(float(ipc), 4)
        f.close()
    return prefetcher_ipc, traces

def draw_results(results, traces, baseline):
    bar_width = 0.15
    color = ['r', 'b', 'y', 'g', 'c', 'm', 'y']
    xticks = np.arange(len(traces))

    index = 0
    for result in results:
        y = []
        for trace in traces:
            if trace in results[result]:
                y.append(results[result][trace] / baseline[trace] - 1)
            else:
                y.append(0)
        plt.bar(xticks + index * bar_width, height=y, width=bar_width, color=color[index], label=result)
        #plt.bar(xticks + index * bar_width, height=y, width=bar_width, color=color[index])
        index += 1

    plt.legend()
    plt.xticks(xticks, traces, rotation=90)
    plt.show()

def calculateImprovement(result, baseline, traces):
    whole_improvement = 0
    for trace in traces:
        whole_improvement += result[trace] / baseline[trace] - 1
    return whole_improvement / len(traces)

def addNewResults(result, baseline, traces):
    ipcs, result_traces = getContentsFromTargetPrefetcher(result)
    global results
    results[result] = ipcs
    print(result, calculateImprovement(ipcs, baseline, traces))

results = {}
print("read results ...")

baseline, traces = getContentsFromTargetPrefetcher("baseline")
addNewResults("ipcp", baseline, traces)
addNewResults("page_change_5", baseline, traces)
addNewResults("page_change_4", baseline, traces)



print("start analysis ...")

#remove not in classify
# useful_traces = []
# for trace in traces:
#     if trace in results["page_change_5"]:
#         useful_traces.append(trace)

draw_results(results, traces, baseline)

# print("...")
# change = 0
# useful = 0
# damage = 0
# whole_num = 0
# performance_well_traces = []
# for trace in traces:
#     whole_num += 1
#     if results["ipcp"][trace] != results["page_change_4"][trace]:
#         change += 1
#     if results["ipcp"][trace] > results["page_change_4"][trace]:
#         print(trace)
#         damage += 1
#     if results["ipcp"][trace] < results["page_change_4"][trace]:
#         useful += 1
#         performance_well_traces.append(trace)
# print("whole_num", whole_num)
# print("change", change)
# print("damage", damage)
# print("useful", useful)
#
#
# results = {}
# addNewResults("ipcp", baseline, performance_well_traces)
# addNewResults("page_change_5", baseline, performance_well_traces)
# addNewResults("page_change_4", baseline, performance_well_traces)








