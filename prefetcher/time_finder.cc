//
// Created by Umasou on 2021/6/23.
//

#include "time_finder.h"
#include "cache.h"
#include "log.h"
//ChampSimLog cslog("fix_time.txt");

uint64_t Time_finder::find_next_addr(uint64_t ip, uint64_t addr) {
    if (this->time_recorder.find(ip) != this->time_recorder.end()){
        for (auto addr_it : this->time_recorder[ip]) {
            if (addr == addr_it.start_addr){
                return addr_it.next_addr.addr;
            }
        }
    }
    return -1;
}

vector<uint64_t> Time_finder::predict(uint64_t ip, uint64_t cache_line) {
    vector<uint64_t> pf_addrs;
    if (this->time_recorder.find(ip) != this->time_recorder.end()){
        uint64_t start_addr = cache_line;
        for (int i = 0; i < PREFETCH_DEGREE; ++i) {
            uint64_t next_addr = this->find_next_addr(ip, start_addr);
            if (-1 == next_addr){
                break;
            }
            else{
                pf_addrs.push_back(next_addr);
                start_addr = next_addr;
            }
        }
    }
    return pf_addrs;
}

void Time_finder::update_ip_last_addr(uint64_t ip, uint64_t addr) {
    //增加ip选择的功能，可以参考wuhao(micro 19)
    this->ip_last_addr[ip] = addr;
}



void Time_finder::update_time_recorder(uint64_t ip, uint64_t start_addr, uint64_t next_addr) {
    //is first addr there?
//    int index = -1;
//    for (int i = 0; i < this->time_recorder[ip].size(); ++i) {
//        if (this->time_recorder[ip][i].start_addr == start_addr){
//            index = i;
//            break;
//        }
//    }
//    if (index != -1) {
//        this->time_recorder[ip][index].next_addr.addr = next_addr;
//        this->time_recorder[ip][index].next_addr.conf = DEFAULT_CONF;
//    }
//    else {
//        Next_addr nextAddr;
//        nextAddr.addr = next_addr;
//        nextAddr.conf = DEFAULT_CONF;
//        Addr_pair addrPair;
//        addrPair.start_addr = start_addr;
//        addrPair.next_addr = nextAddr;
//        addrPair.lru = 0;
//        this->time_recorder[ip].push_back(addrPair);
//    }

    //increase others lru
    for (auto it : this->time_recorder[ip]) {
        it.lru += 1;
    }
    //is first addr there?
    int index = -1;
    for (int i = 0; i < this->time_recorder[ip].size(); ++i) {
        if (this->time_recorder[ip][i].start_addr == start_addr){
            index = i;
            break;
        }
    }
    if (index != -1){
        this->time_recorder[ip][index].lru = 0;
        //is same pair?
        if (this->time_recorder[ip][index].next_addr.addr == next_addr){
            if (this->time_recorder[ip][index].next_addr.conf < DEFAULT_CONF){
                this->time_recorder[ip][index].next_addr.conf += 1;
            }
        }
        else{
            if (this->time_recorder[ip][index].next_addr.conf == 0){
                this->time_recorder[ip][index].next_addr.addr = next_addr;
                this->time_recorder[ip][index].next_addr.conf = DEFAULT_CONF;
            }
            else{
                this->time_recorder[ip][index].next_addr.conf -= 1;
            }
        }
    }
    else{
        //is not full
        if (this->time_recorder[ip].size() < ENTRY_NUM){
            Next_addr nextAddr;
            nextAddr.addr = next_addr;
            nextAddr.conf = DEFAULT_CONF;
            Addr_pair addrPair;
            addrPair.start_addr = start_addr;
            addrPair.next_addr = nextAddr;
            addrPair.lru = 0;
            this->time_recorder[ip].push_back(addrPair);
        }
        else{
            //find victim
            int victim_index = 0;
            for (int i = 0; i < this->time_recorder[ip].size(); ++i) {
                if (this->time_recorder[ip][i].lru > this->time_recorder[ip][victim_index].lru){
                    victim_index = i;
                }
            }
            //add new pair
            Next_addr nextAddr;
            nextAddr.addr = next_addr;
            nextAddr.conf = DEFAULT_CONF;
            this->time_recorder[ip][victim_index].lru = 0;
            this->time_recorder[ip][victim_index].start_addr = start_addr;
            this->time_recorder[ip][victim_index].next_addr = nextAddr;
        }
    }
}


void Time_finder::train(uint64_t ip, uint64_t cache_line, uint64_t page) {
    //need to update?(只记录换页的?)
    if (this->ip_last_addr.find(ip) != this->ip_last_addr.end()){
        uint64_t last_addr = this->ip_last_addr[ip];
        uint64_t last_page = last_addr >> LOG2_PAGE_SIZE;
        if (last_page == page){
            this->update_ip_last_addr(ip, cache_line);
            return;
        }
        else{
            //考虑增加动态调整DEGREE的功能，所以先分开
            uint64_t pref_next_addr = this->find_next_addr(ip, last_addr);
            //same
            if (-1 == pref_next_addr){
                this->update_time_recorder(ip, last_addr, cache_line);
            }
            else if (pref_next_addr == cache_line){
                this->update_time_recorder(ip, last_addr, cache_line);
            }
            else{
                this->update_time_recorder(ip, last_addr, cache_line);
            }
        }
    }
    this->update_ip_last_addr(ip, cache_line);

}



