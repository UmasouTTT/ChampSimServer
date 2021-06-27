//
// Created by Umasou on 2021/6/24.
//

#include "ip_classifier.h"
#include "cache.h"

void Ip_classifier::update_when_ip_is_full() {
    auto victim = this->ip_jump.begin();
    for (auto it : this->ip_jump) {
        if (it.second.second < victim->second.second){
            victim = it;
        }
    }
    this->ip_jump.erase(victim);
    this->ip_last_page.erase(victim->first);
}

void Ip_classifier::update_important_ips(uint64_t ip) {
    if (this->important_ip_map.find(ip) == this->important_ip_map.end()){
        //lru
        for (auto it : this->important_ip_map) {
            it.second += 1;
        }
        if (this->important_ip_map.size() == IMPORTANT_IPS_SIZE){
            auto victim = this->important_ip_map.begin();
            for (auto it : this->important_ip_map) {
                if (it.second > victim->second){
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
        if (page == last_page){
            this->ip_jump[ip].first -= 1;
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

