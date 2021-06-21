import os
import matplotlib.pyplot as plt
import numpy as np

def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def getContentsFromTargetPrefetcher(results):
    print(results)
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

results = {}
print("read results ...")
# only_seperate_train, traces = getContentsFromTargetPrefetcher("only_seperate_train")
# sep_ip_and_train, traces = getContentsFromTargetPrefetcher("sep_ip_and_train")
# absolute_train, traces = getContentsFromTargetPrefetcher("absolute_train")
# kaichao, traces = getContentsFromTargetPrefetcher("kaichao")
# kaichao_formal, traces = getContentsFromTargetPrefetcher("kaichaoformal")
# l1_l2_both_important, traces = getContentsFromTargetPrefetcher("l1_l2_both_important")
# l1_most_l2_less, traces = getContentsFromTargetPrefetcher("l1_most_l2_less")

ipcp, traces = getContentsFromTargetPrefetcher("ipcp")
baseline, traces = getContentsFromTargetPrefetcher("baseline")
page_change_5, traces = getContentsFromTargetPrefetcher("page_change_5")

# ipcp_compatition, traces = getContentsFromTargetPrefetcher("ipcp_compatition")
# ipcp_com_classify, traces = getContentsFromTargetPrefetcher("ipcp_com_classify")

#ipcp_paper_l1l2_onlyl1train, traces = getContentsFromTargetPrefetcher("ipcp_paper_l1l2_onlyl1train")

# results["no_calssify"] = only_seperate_train
# results["classify"] = sep_ip_and_train
# results["absolute_train"] = absolute_train
# results["kaichao"] = kaichao
# results["kaichao_formal"] = kaichao_formal
# results["l1_l2_both_important"] = l1_l2_both_important
# results["l1_most_l2_less"] = l1_most_l2_less
# results["ipcp_compatition"] = ipcp_compatition
# results["ipcp_com_classify"] = ipcp_com_classify
#results["ipcp_paper_l1l2_onlyl1train"] = ipcp_paper_l1l2_onlyl1train

results["baseline"] = baseline
results["ipcp"] = ipcp
results["page_change_5"] = page_change_5


print("start analysis ...")

#remove not in classify
useful_traces = []
for trace in traces:
    if trace in results["page_change_5"]:
        useful_traces.append(trace)

draw_results(results, useful_traces, baseline)

print("...")
change = 0
useful = 0
damage = 0
whole_num = 0
performance_well_traces = []
for trace in traces:
    whole_num += 1
    if results["ipcp"][trace] != results["page_change_5"][trace]:
        change += 1
    if results["ipcp"][trace] > results["page_change_5"][trace]:
        print(trace)
        damage += 1
    if results["ipcp"][trace] < results["page_change_5"][trace]:
        useful += 1
        performance_well_traces.append(trace)
print("whole_num", whole_num)
print("change", change)
print("damage", damage)
print("useful", useful)


#improvement
print("ipcp", calculateImprovement(ipcp, baseline, traces))
print("page_change_5", calculateImprovement(page_change_5, baseline, traces))
# print("ipcp_compatition", calculateImprovement(ipcp_compatition, baseline, traces))
# print("ipcp_com_classify", calculateImprovement(ipcp_com_classify, baseline, traces))
# print("no_calssify", calculateImprovement(only_seperate_train, baseline, useful_traces))
# print("calssify", calculateImprovement(sep_ip_and_train, baseline, useful_traces))

# print("kaichao", calculateImprovement(kaichao, baseline, useful_traces))
# print("kaichao_formal", calculateImprovement(kaichao_formal, baseline, useful_traces))
# print("absolute_train", calculateImprovement(absolute_train, baseline, useful_traces))




