//
// Created by Umasou on 2021/6/23.
//

#include "time_finder.h"
#include "cache.h"
#include "log.h"

/**
 *参数：需要替换的ip
 *操作：把参数中ip的 历史addr对、最后访问的addr 删除
 **/
void Time_finder::repl_ip(vector<uint64_t> erase_ips){
    //更新逻辑过于暴力,可以修改
    //erase
    for (auto it : erase_ips) {
        this->time_recorder.erase(it);
        this->ip_last_addr.erase(it);
    }

}

/**
 * 参数：ip 和 本次访问的address（还是对应的cache_line）
 * 返回值：该ip历史情况访问地址对中 key为addr时，下一个最有可能访问的地址，如果不存在，则返回-1
 * 问题：是否需要判断一下 置信度
 **/
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

/**
 * 参数：ip 和 本次访问address对应的 cache_line
 * 返回值：预测需要预取的address（或cache_line）集合
 * 问题：是否返回值中会有重复的
 **/
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

/**
 * 参数：本次访问的ip 和 address
 * 操作：更新ip最后访问的address
 **/
void Time_finder::update_ip_last_addr(uint64_t ip, uint64_t addr) {
    //增加ip选择的功能，可以参考wuhao(micro 19)
    this->ip_last_addr[ip] = addr;
}

/**
 * 前提：本次访问ip一定记录过对应的历史访问信息
 * 参数：本次访问的ip 开始地址 和 下一个地址
 * 操作：用于更新该ip对应的 记录pattern信息的 成员
 **/
void Time_finder::update_time_recorder(uint64_t ip, uint64_t start_addr, uint64_t next_addr) {
    //increase others lru

    //is first addr there?
    int index = -1;
    for (int i = 0; i < this->time_recorder[ip].size(); ++i) {
        if (this->time_recorder[ip][i].start_addr == start_addr){
            index = i;
            break;
        }
    }
    if (index != -1){//历史记录过该ip对应该start_addr的下一个访问地址
        this->time_recorder[ip][index].lru = 0;
        //is same pair?
        if (this->time_recorder[ip][index].next_addr.addr == next_addr){
            if (this->time_recorder[ip][index].next_addr.conf < DEFAULT_CONF){
                this->time_recorder[ip][index].next_addr.conf += 1;
            }
            //lru ???
            for (auto it : this->time_recorder[ip]) {
                it.lru += 1;
            }
            this->time_recorder[ip][index].lru = 0;
        }
        else{
            if (this->time_recorder[ip][index].next_addr.conf == 0){
                this->time_recorder[ip][index].next_addr.addr = next_addr;
                this->time_recorder[ip][index].next_addr.conf = DEFAULT_CONF;
                //lru
                for (auto it : this->time_recorder[ip]) {
                    it.lru += 1;
                }
                this->time_recorder[ip][index].lru = 0;

            }
            else{

                this->time_recorder[ip][index].next_addr.conf -= 1;
            }
        }
    }
    else{//从来没有记录过该ip对应start_addr的下一个访问地址
        for (auto it : this->time_recorder[ip]) {
            it.lru += 1;
        }
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

/**
 * 功能：时间流的训练
 * 参数：本次访问的 ip cache_line page等信息
 * 具体操作：只对换页情况的ip进行训练（更新此ip的pattern）
 **/
void Time_finder::train(uint64_t ip, uint64_t cache_line, uint64_t page,  vector<uint64_t> erase_time_ips) {
    this->repl_ip(erase_time_ips);//删除参数erase_time_ips中所有ip记录的历史访问信息
    //need to update?(只记录换页的?)
    if (this->ip_last_addr.find(ip) != this->ip_last_addr.end()){
        uint64_t last_addr = this->ip_last_addr[ip];
        uint64_t last_page = last_addr >> LOG2_PAGE_SIZE;
        //如果没有换页，认为不是时间流，不进行训练
        if (last_page == page){
            this->update_ip_last_addr(ip, cache_line);
            return;
        }
        //否则进行训练（即更新该ip对应的pattern）
        else{
            //考虑增加动态调整DEGREE的功能，所以先分开(wuhao MICRO 19)
            uint64_t pref_next_addr = this->find_next_addr(ip, last_addr);
            //same
            if (-1 == pref_next_addr){//这里应该有问题吧，如果是-1的话，直接调用updata_time_recorder会出错
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



