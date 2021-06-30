//
// Created by Umasou on 2021/6/24.
//

#include "ip_classifier.h"
#include "cache.h"

/**
 *功能：当存储信息满了，删除一个换页最不频繁ip对应的存储信息 
 **/
void Ip_classifier::update_when_ip_is_full() {
    map<uint64_t, pair<uint64_t, uint64_t>>::iterator victim = this->ip_jump.begin();
    for (map<uint64_t, pair<uint64_t, uint64_t>>::iterator it = this->ip_jump.begin() ; it != this->ip_jump.end(); it++) {
        if (it->second.first < victim->second.first){
            victim = it;
        }
    }
    this->ip_jump.erase(victim);
    this->ip_last_page.erase(victim->first);
}

/**
 * 功能：对新的具有时间特性的ip进行信息的更新，主要是将其存入important_ip_map以及new_time_ips中，必要时，删除被替换的ip
 **/
void Ip_classifier::update_important_ips(uint64_t ip) {
    if (this->important_ip_map.find(ip) == this->important_ip_map.end()){
        //lru
        for (auto it : this->important_ip_map) {//更新计数器
            it.second += 1;
        }
        if (this->important_ip_map.size() == IMPORTANT_IPS_SIZE){//如果满了，寻找需要替换的位置
            auto victim = this->important_ip_map.begin();
            for (auto it = this->important_ip_map.begin(); it != this->important_ip_map.end(); it++) {
                if (it -> second > victim->second){
                    victim = it;
                }
            }
            this->important_ip_map.erase(victim);
            this->erase_ips.push_back(victim->first);
        }
        this->important_ip_map[ip] = 0;
        this->new_time_ips.push_back(ip);
    }
    else{
        this->important_ip_map[ip] = 0;
    }
}

/**
 * 
 **/
void Ip_classifier::update(uint64_t ip, uint64_t addr) {
    this->new_time_ips.clear();
    this->erase_ips.clear();
    //update
    uint64_t page = addr >> LOG2_PAGE_SIZE;
    //new
    if (this->ip_last_page.find(ip) == this->ip_last_page.end()){
        if (this->ip_jump.size() == IP_NUM){
            this->update_when_ip_is_full();
        }
        this->ip_last_page[ip] = page;
        this->ip_jump[ip] = make_pair(0, 1);
        return;
    }
    else{
        //
        uint64_t last_page = this->ip_last_page[ip];
        if (page == last_page){//没有换页
            this->ip_jump[ip].first -= 1;//为什么要减一？
            this->ip_jump[ip].second += 1;
            //kong jian
            if (this->ip_jump[ip].first < VICTIM_THRESHOLD ){
                this->ip_jump.erase(ip);
                this->ip_last_page.erase(ip);
                if (this->important_ip_map.find(ip) != this->important_ip_map.end()){
                    this->important_ip_map.erase(ip);
                    this->erase_ips.push_back(ip);
                }
            }
        }
        else{
            this->ip_jump[ip].first += 1;
            this->ip_jump[ip].second += 1;
            //shi jian
            if (this->ip_jump[ip].first > FINISH_THRESHOLD){
                this->ip_jump.erase(ip);
                this->ip_last_page.erase(ip);
                this->update_important_ips(ip);
            }
        }
    }
}


vector<uint64_t> Ip_classifier::get_important_ips() {
    vector<uint64_t> important_ip_vec;
    for (auto it : this->important_ip_map) {
        important_ip_vec.push_back(it.first);
    }
    return important_ip_vec;
}

