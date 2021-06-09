import os
def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces]

def getContentsFromTargetPrefetcher(prefetcher, results):
    prefetcher_result = {}
    prefetcher_important = {}
    for result in results:
        if prefetcher in result:
            f = open(result, "r+", encoding="utf-8")
            start_record = False
            prefetcher_result[result.split('/')[-1].split(".champ")[0]] = ""
            important_detail = []
            for line in f:
                if "L1D PREFETCH  REQUESTED:" in line:
                    important_detail.append(line.strip() + "\n")
                if "L2C PREFETCH  REQUESTED:" in line:
                    important_detail.append(line.strip() + "\n")
                if "CPU 0 cumulative IPC:" in line:
                    ipc = line.split(" ")[4]
                    important_detail.append("ipc:{}".format(ipc) + "\n")
                if "DRAM Statistics" in line:
                    break
                if start_record:
                    prefetcher_result[result.split('/')[-1].split(".champ")[0]] += line
                if "Region of Interest Statistics" in line:
                    start_record = True
            prefetcher_important[result.split('/')[-1].split(".champ")[0]] = important_detail
            f.close()
    return prefetcher_result, prefetcher_important

compare_results = "compare"
results = get_files("../../../PycharmProjects/pythonProject/results_200M")
classifier, calssifier_important = getContentsFromTargetPrefetcher("ip_classifier", results)
baseline, baseline_important = getContentsFromTargetPrefetcher("ipcp-ipcp-ipcp", results)
#detail
# for result in classifier:
#     if result in baseline:
#         dir = "compareClassiferAndIPCP/{}".format(result)
#         if not os.path.exists(dir):
#             os.mkdir(dir)
#         f = open(dir + "/classify", "w+", encoding="utf-8")
#         f.write(classifier[result])
#         f.close()
#         f = open(dir + "/ipcp", "w+", encoding="utf-8")
#         f.write(baseline[result])
#         f.close()
#ipc
f = open("compareClassiferAndIPCP/{}".format("compare"), "w+", encoding="utf-8")
for result in classifier:
    if result in baseline:
        f.write("trace:{}\n".format(result))
        f.write("ipcp\n")
        for detail in baseline_important[result]:
            f.write(detail)
        f.write("classify\n")
        for detail in calssifier_important[result]:
            f.write(detail)
f.close()

