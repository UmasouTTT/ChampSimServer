//
// Created by Umasou on 2021/6/24.
//

#ifndef CHAMPSIMSERVER_IP_CLASSIFIER_H
#define CHAMPSIMSERVER_IP_CLASSIFIER_H

#include <map>
#include <iostream>
#include <vector>

#define FINISH_THRESHOLD 5
#define IMPORTANT_IPS_SIZE 5
#define IP_NUM 64 //考虑跟空间一起存放，减少资源需要
#define VICTIM_THRESHOLD -5
using namespace std;

class Ip_classifier{

public:
    void update(uint64_t ip, uint64_t addr);

    vector<uint64_t> get_important_ips();

    vector<uint64_t> get_erase_time_ip(){return this->erase_ips;}
    vector<uint64_t> get_new_time_ip(){return this->new_time_ips;}

private:
    void update_when_ip_is_full();

    void update_important_ips(uint64_t ip);

    map<uint64_t, pair<uint64_t, uint64_t>> ip_jump;//该ip换页的次数&总的次数
    map<uint64_t, uint64_t> ip_last_page;//记录ip上次访问的页面
    map<uint64_t, uint64_t> important_ip_map;//记录当前学习到的具有时间特征的ip集合，value为lru计数器
    vector<uint64_t> new_time_ips;
    vector<uint64_t> erase_ips;
};

#endif //CHAMPSIMSERVER_IP_CLASSIFIER_H
