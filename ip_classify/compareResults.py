import os
from py_tool.draw_pic import DrawBar

def get_files(path):
    traces = os.listdir(path)
    return [path + "/" + trace for trace in traces], traces

def readResults(experiment_results, prefetchers, log_path):
    results = {}
    for result in experiment_results:
        results[result.split("/")[-1]] = {}
        f = open(result, "r+", encoding="utf-8")
        for line in f:
            content = line.strip().split(" : ")
            trace_name = content[0]
            ipc = content[1]
            results[result.split("/")[-1]][trace_name] = float(ipc)
        f.close()




    #remove not useful
    traces = set()
    for prefetcher in results:
        for trace in results[prefetcher]:
            traces.add(trace)

    f = open(log_path, "w+", encoding="utf-8")
    for trace in traces:
        print(trace)
        baseline = results["baseline"][trace]
        a = 0
        b = 0
        c = 0
        if trace in results["ipcp"]:
            a = round(results["ipcp"][trace] / baseline, 2)
        if trace in results["no_classifier"]:
            b = round(results["no_classifier"][trace] / baseline, 2)
        c = round(results["with_classifier"][trace] / baseline,2)
        print(baseline,a, b, c)
        f.write("{}: {}:{}, {}:{}, {}:{}".format(trace, "ipcp",a,"no_classifier",b,"with_classifier", c ) + "\n")
    f.close()
    trace_compare = {}
    for trace in traces:
        temp = []
        for prefetcher in prefetchers:
            if trace in results[prefetcher]:
                temp.append(results[prefetcher][trace])
        if len(temp) == len(prefetchers):
            trace_compare[trace] = temp
    return trace_compare, prefetchers

paths, prefetchers = get_files("prefetcher_results")
results, prefetchers = readResults(paths, prefetchers, "compare")


x = []
y = []
for trace in results:
    x.append(trace)

for prefetcher in range(len(prefetchers)):
    temps = []
    for trace in results:
        temps.append(results[trace][prefetcher])
    y.append(temps)

print(prefetchers)
draw_bar = DrawBar(x, y, prefetchers)
draw_bar.draw()
a  =1

