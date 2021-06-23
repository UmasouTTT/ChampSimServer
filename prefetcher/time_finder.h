//
// Created by Umasou on 2021/6/23.
//

#ifndef CHAMPSIMSERVER_TIME_FINDER_H
#define CHAMPSIMSERVER_TIME_FINDER_H

#include <iostream>
#include <map>
#include <vector>

using namespace std;

#define ENTRY_NUM 10
//改成动态调整的形式
#define PREFETCH_DEGREE 3
#define DEFAULT_CONF 3

struct Next_addr{
    uint64_t addr;
    int conf;
};

struct Addr_pair{
    uint64_t start_addr;
    Next_addr next_addr;
    int lru;
    bool valid;
};

class Time_finder{

public:
    Time_finder(){};
    void train(uint64_t ip, uint64_t cache_line, uint64_t page);
    vector<uint64_t> predict(uint64_t ip, uint64_t cache_line);

private:
    void update_time_recorder(uint64_t ip, uint64_t start_addr, uint64_t next_addr);
    void update_ip_last_addr(uint64_t ip, uint64_t addr);
    uint64_t find_next_addr(uint64_t ip, uint64_t addr);
    map<uint64_t, vector<Addr_pair>> time_recorder;
    map<uint64_t, uint64_t> ip_last_addr;

};

#endif //CHAMPSIMSERVER_TIME_FINDER_H
