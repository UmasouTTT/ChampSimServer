

def get_ip_values(path):
    ip_value = {}
    f = open(path, "r+", encoding="utf-8")
    for line in f:
        #ip: 4249044 value :1.000000appear : 2hit :2
        content = line.strip().split(":")
        ip = content[1].replace(" ","").replace("value", "")
        value = round(float(content[2].replace("appear ", "")), 2)
        appear = int(content[3].replace(" ", "").replace("hit", ""))
        hit = int(content[4])
        ip_value[ip] = [value, appear, hit]
    f.close()
    return ip_value

def find_useful_ip(ip_values):
    value_ips = []
    for ip in ip_values:
        if ip_values[ip][0] >= 0.9:
            value_ips.append(ip)
            #print(ip_values[ip])
        # elif ip_values[ip][2] > 5000:
        #     value_ips.append(ip)
            #print(ip_values[ip])
        else:
            print(ip_values[ip])
    print([int(ip) for ip in value_ips])


find_useful_ip(get_ip_values("ip_value_log.txt"))
