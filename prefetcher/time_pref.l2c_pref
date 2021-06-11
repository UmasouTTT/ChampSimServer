//
// Created by 崔凯朝 on 2021/3/2.
//

#include "cache.h"

#include <bits/stdc++.h>

using namespace std;
//#define Dynamic_Adjustment
#define MAX_COUNT 3
#define POWER_A 0.5
#define POWER_B 0.5

#define PC_WIDTH  18
#define ADDR_WIDTH  18

#define train_all 1//0最好

const double L2_THRESHOLD_UP_HIT_RATE= 0.7;
const double L2_THRESHOLD_DOWN_HIT_RATE=0.3;
const double UP_HIT_RATE=0.9;
const double DOWN_HIT_RATE=0.15;


#define PREFETCH_DEGREE 6
#define PREFETCH_DEGREE_MAX 12
#define PREFETCH_DEGREE_MIN 3

#define L2_THRESHOLD 0.6//没用
#define LLC_THRESHOLD 0.2//没用
#define L2_MAX_THRESHOLD 1
#define L2_MIN_THRESHOLD 0.2
#define LLC_MAX_THRESHOLD 1
#define LLC_MIN_THRESHOLD 0.2

//Filter Table
#define FILTER_TABLE_SIZE 64
#define LOG2_FILTER_TABLE_SIZE 6

//Signature Table
#define SIGNATURE_DELTA_SIZE 4
#define SIGNATURE_CONF_MAX 7
#define SIGNATURE_TABLE_SET  128
#define LOG2_SIGNATURE_TABLE_SET 7
#define SIGNATURE_TABLE_WAY 1
#define SIGNATURE_BITS 7
#define LEFT_MOVE_BITS 3

//Recent request
#define RECENT_REQUEST_SIZE 64//在二级cache预取中有用

//Delay Queue
#define DELAYQSIZE 1024//没用
#define DELAY 0//L2敏感
#define TIME_BITS 12

//IP table
#define IP_TABLE_SET 1024
#define LOG2_IP_TABLE_SET 10
#define IP_TABLE_WAY 1
#define PAGE_BITS 2//没用
#define IP_DELTA_SIZE 4
#define IP_CONF_MAX 7

bool SAMEPAGE(uint64_t lineaddr1,uint64_t lineaddr2)
{
    return ((((lineaddr1) ^ (lineaddr2)) >> (LOG2_PAGE_SIZE-LOG2_BLOCK_SIZE)) == 0);
}

uint64_t TRUNCATE(uint64_t x,uint64_t nbits)
{
    return (((x) & ((1<<(nbits))-1)));
}

#define INCREMENT(x,n) {x++; if (x==(n)) x=0;}

enum ReplType
{
    REPL_MY,
    REPL_LRU,
    REPL_LFU,
    REPL_HAWKEYE,
    REPL_PERFECT
};

struct ReplMetrics
{
public:
    struct replMy{
        uint64_t count;
        uint64_t valid;
        replMy():count(0),valid(0){}
    };
    replMy my;
    uint64_t lru;
    uint64_t lfu;
    uint64_t hawkeye;
    uint64_t perfect;
    ReplMetrics():my(),lru(0),lfu(0),hawkeye(0),perfect(0){}

};//变量repl_metrics

template<typename T1,typename  T2> class Repl     //T1是 索引类型， T2是索引对应存储的元数据
{
protected:
    vector<map<T1,T2>>* entry_list;
//ReplType  type;
public:
    Repl(vector<map<T1,T2>>* entry):entry_list(entry){}
    virtual void setEntry(uint64_t set_id,T1 tag)=0;
    virtual T1 findVictim(uint64_t set_id)=0;
    static Repl<T1,T2>* create_repl(vector<map<T1,T2>> *entry,ReplType type);
};

template<typename T1,typename  T2> class ReplMy : public  Repl<T1,T2>
{
public:
    ReplMy(vector<map<T1,T2>>* entry):Repl<T1,T2>(entry){}

    void setEntry(uint64_t set_id,T1 tag)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto it=entry_map.find(tag);
        assert(it!=entry_map.end());
        if(it->second.repl_metrics.my.count>=MAX_COUNT)
        {
            for(auto  jt=entry_map.begin();jt!=entry_map.end();jt++)
            {
                jt->second.repl_metrics.my.count=((jt->second.repl_metrics.my.count)>>1);
                jt->second.repl_metrics.my.valid=((jt->second.repl_metrics.my.valid)>>1);
            }
        }
        ++(it->second.repl_metrics.my.count);
    }

    T1 findVictim(uint64_t set_id)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto victim_it=entry_map.begin();
        for(auto it=entry_map.begin();it!=entry_map.end();++it)
        {
            if(it->second.repl_metrics.my.count*POWER_A+it->second.repl_metrics.my.valid*POWER_B < victim_it->second.repl_metrics.my.count*POWER_A+victim_it->second.repl_metrics.my.valid*POWER_B)
            {
                victim_it=it;
            }
        }
        assert(victim_it!=entry_map.end());
        T1 tag=victim_it->first;
        return tag;
    }
};

template<typename T1,typename T2>class ReplLRU: public  Repl<T1,T2>
{
public:
    ReplLRU(vector<map<T1,T2>>* entry):Repl<T1,T2>(entry){}

    void setEntry(uint64_t set_id,T1 tag)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto it=entry_map.find(tag);
        assert(it!=entry_map.end());
        for(auto jt=entry_map.begin();jt!=entry_map.end();jt++)
        {
            ++(jt->second.repl_metrics.lru);
        }
        it->second.repl_metrics.lru=0;
    }

    T1 findVictim(uint64_t set_id)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto victim_it=entry_map.begin();
        for(auto it=entry_map.begin();it!=entry_map.end();++it)
        {
            if(it->second.repl_metrics.lru > victim_it->second.repl_metrics.lru)
            {
                victim_it=it;
            }
        }
        assert(victim_it!=entry_map.end());
        T1 tag=victim_it->first;
        return tag;
    }
};

template<typename T1,typename T2>class ReplLFU:public Repl<T1,T2>
{
public:
    ReplLFU(vector<map<T1,T2>>* entry):Repl<T1,T2>(entry){}

    void setEntry(uint64_t set_id,T1 tag)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto it=entry_map.find(tag);
        assert(it!=entry_map.end());
        ++(it->second.repl_metrics.lfu);
    }

    T1 findVictim(uint64_t set_id)
    {
        map<T1,T2> &entry_map=(*(Repl<T1,T2>::entry_list))[set_id];
        auto victim_it=entry_map.begin();
        for(auto it=entry_map.begin();it!=entry_map.end();++it)
        {
            if(it->second.repl_metrics.lfu < victim_it->second.repl_metrics.lfu)
            {
                victim_it=it;
            }
        }
        assert(victim_it!=entry_map.end());
        T1 tag=victim_it->first;
        return tag;
    }
};

template<typename T1,typename T2>class ReplHawkeye:public Repl<T1,T2>
{
public:
    ReplHawkeye(vector<map<T1,T2>>* entry):Repl<T1,T2>(entry){}

    void setEntry(uint64_t set_id,T1 tag)
    {

    }

    T1 findVictim(uint64_t set_id)
    {
        return 0;
    }
};

template<typename T1,typename T2>class ReplPerfect:public Repl<T1,T2>
{
public:
    ReplPerfect(vector<map<T1,T2>>* entry):Repl<T1,T2>(entry){}

    void setEntry(uint64_t set_id,T1 tag)
    {

    }

    T1 findVictim(uint64_t set_id)
    {
        return 0;
    }

};

template<typename T1,typename T2>
Repl<T1,T2>* Repl<T1,T2>::create_repl(vector<map<T1,T2>> *entry,ReplType type)
{
    Repl<T1,T2> *repl=nullptr;
    switch(type)
    {
        case REPL_MY:
            repl=new ReplMy<T1,T2>(entry);
            break;
        case REPL_LRU:
            repl=new ReplLRU<T1,T2>(entry);
            break;
        case REPL_LFU:
            repl=new ReplLFU<T1,T2>(entry);
            break;
        case REPL_HAWKEYE:
            repl=new ReplHawkeye<T1,T2>(entry);
            break;
        case REPL_PERFECT:
            repl=new ReplPerfect<T1,T2>(entry);
            break;
        default:
            assert(0);
    }
    return repl;
}

/* 替换策略架构完成*/

/*过滤表*/
class FilterTable
{
public:
    FilterTable():data(){}

    bool insert(uint64_t addr)
    {
        bool res=true;
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(i->first==addr)
            {
                res=false;
                break;
            }
        }
        if(res)
        {
            while(data.size()>=FILTER_TABLE_SIZE)
            {
                data.pop_front();
            }
            data.push_back(make_pair(addr,false));
        }
        return res;
    }

    void update(uint64_t addr)
    {
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(i->first==addr)
            {
                i->second=true;
            }
        }
    }

    void eviction(uint64_t addr)
    {
        for(auto i=data.begin();i!=data.end();)
        {
            if(i->first==addr)
            {
                i=data.erase(i);
            }
            else
                i++;
        }
    }

    double get_reduce()
    {
        double useful=0;
        if(data.empty())
            return 1;
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(i->second)
                useful++;
        }
        return useful/data.size();
    }

    void reset()
    {
        data.clear();
    }
private:
    deque<pair<uint64_t,bool>> data;
};

//Signature Table
struct SignatureTableEntry
{
public:
    map<int,uint64_t> data;
    ReplMetrics repl_metrics;

    SignatureTableEntry():data(),repl_metrics(){}

    void insert(int delta)
    {
        if(delta==0)
            return;
        if(data.find(delta)==data.end())
        {
            uint64_t cur_conf=0;
            while(data.size()>=SIGNATURE_DELTA_SIZE)
            {
                int victim_delta=find_victim();
                // cur_conf=data[victim_delta];
                data.erase(victim_delta);
            }
            data.insert(make_pair(delta,cur_conf));
        }
        increase(delta);
    }

    vector<pair<int,double>> get_info()
    {
        vector<pair<int,double>> res;
        double sum=0;
        if(data.empty())
            return res;
        for(auto i=data.begin();i!=data.end();i++)
        {
            sum+=i->second;
        }
        for(auto i=data.begin();i!=data.end();i++)
        {
            res.push_back(make_pair(i->first,i->second/sum));
        }
        return res;
    }

private:
    int find_victim()
    {
        int victim_delta=data.begin()->first;
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(i->second<data[victim_delta])
                victim_delta=i->first;
        }
        return victim_delta;
    }

    void increase(int delta)
    {
        assert(data.find(delta)!=data.end());
        if(data[delta]>=SIGNATURE_CONF_MAX)
        {
            for(auto i=data.begin();i!=data.end();i++)
            {
                i->second=((i->second)>>1);
            }
        }
        data[delta]++;
    }

};

class SignatureTable{
public:
    SignatureTable():data(SIGNATURE_TABLE_SET)
    {
        repl=Repl<uint64_t,SignatureTableEntry>::create_repl(&data,REPL_LRU);
    }

    void update(uint64_t signature,int delta)
    {
        uint64_t set_id=TRUNCATE(signature,LOG2_SIGNATURE_TABLE_SET);
        uint64_t tag=(signature>>LOG2_SIGNATURE_TABLE_SET);
        if(data[set_id].find(tag)==data[set_id].end())
        {
            while(data[set_id].size()>=SIGNATURE_TABLE_WAY)
            {
                uint64_t victim_tag=repl->findVictim(set_id);
                data[set_id].erase(victim_tag);
            }
            data[set_id].insert(make_pair(tag,SignatureTableEntry()));
        }
//        if(data[set_id][tag].delta==delta)
//        {
//            data[set_id][tag].conf++;
//            if(data[set_id][tag].conf>SIGNATURE_CONF_MAX)
//                data[set_id][tag].conf=SIGNATURE_CONF_MAX;
//        }
//        else
//        {
//            if(data[set_id][tag].conf==0)
//                data[set_id][tag].delta=delta;
//            else
//                data[set_id][tag].conf--;
//        }
        data[set_id][tag].insert(delta);
        repl->setEntry(set_id,tag);
    }

    vector<pair<uint64_t,int>> prefetch(uint64_t signature,uint64_t base_addr,int degree,double fill_l2_threshold,double fill_llc_threshold)
    {
        double prob=1;
        vector<pair<uint64_t,int>> res;
        int pf_degree=0;
        while((prob>=fill_llc_threshold)&&(pf_degree<degree))
        {
            pf_degree++;
            uint64_t set_id=TRUNCATE(signature,LOG2_SIGNATURE_TABLE_SET);
            uint64_t tag=(signature>>LOG2_SIGNATURE_TABLE_SET);
            if(data[set_id].find(tag)==data[set_id].end())
                break;
            vector<pair<int,double>>cur_deltas=data[set_id][tag].get_info();
            sort(cur_deltas.begin(),cur_deltas.end(),[](pair<int,double> i,pair<int,double>j)->bool{return i.second>j.second;});
            if(cur_deltas.empty())
                break;
            for(auto i=0;i<cur_deltas.size();i++)
            {
                if(cur_deltas[i].first==0)
                    continue;
                double cur_prob=cur_deltas[i].second*prob;
                if(cur_prob>=fill_l2_threshold)
                {
                    if(SAMEPAGE(base_addr,base_addr+cur_deltas[i].first))
                    {
                        res.push_back(make_pair(base_addr+cur_deltas[i].first,FILL_L2));
                    }
                }
                else if(cur_prob>=fill_llc_threshold)
                {
                    if(SAMEPAGE(base_addr,base_addr+cur_deltas[i].first))
                    {
                        res.push_back(make_pair(base_addr+cur_deltas[i].first,FILL_LLC));
                    }
                }
                else
                    break;
            }
            if(cur_deltas[0].first==0)
                break;
            if(!SAMEPAGE(base_addr,base_addr+cur_deltas[0].first))
                break;
            prob=cur_deltas[0].second*prob;
            base_addr=base_addr+cur_deltas[0].first;
            signature=update_signature(signature,cur_deltas[0].first);
        }
        return res;
    }

private:
    uint64_t update_signature(uint64_t signature,int delta)
    {
        delta = (delta < 0) ? (((-1) * delta) + (1 << LOG2_BLOCK_SIZE)): delta;
        uint64_t new_signature=bitset<SIGNATURE_BITS>((signature<<LEFT_MOVE_BITS)^delta).to_ullong();
        return new_signature;
    }

    vector<map<uint64_t,SignatureTableEntry>> data;
    Repl<uint64_t,SignatureTableEntry> *repl;
};

//RecentRequest
class RecentRequest{
public:
    struct RecentRequestEntry
    {
        RecentRequestEntry(uint64_t cur_pc=0,uint64_t cur_addr=0):pc(cur_pc),addr(cur_addr){}
        uint64_t pc,addr;
    };

    void insert(uint64_t pc,uint64_t addr)
    {
        while(data.size()>=RECENT_REQUEST_SIZE)
            data.pop_front();
        data.push_back(RecentRequestEntry(pc,addr));
    }

    vector<pair<uint64_t,int>> train(uint64_t pc,uint64_t addr)
    {
        vector<pair<uint64_t,int>> res;
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(SAMEPAGE(i->addr,addr))
            {
                // if(i->pc!=pc)
                // {
                int delta=addr-i->addr;
                res.push_back(make_pair(i->pc,delta));
                // }

            }
        }
        return res;
    }
private:
    deque<RecentRequestEntry> data;
};

//DelayQueue
class DelayQueue
{
public:
    DelayQueue()
    {
        int i;
        for (i=0; i<DELAYQSIZE; i++) {
            lineaddr[i] = 0;
            pc[i]=0;
            cycle[i] = 0;
            valid[i] = 0;
        }
        tail = 0;
        head = 0;
    }

    void dq_push(uint64_t cur_pc,uint64_t  cur_lineaddr,uint64_t current_core_cycle,RecentRequest &rr)
    {
        // enqueue one line address
        if (valid[tail]) {
            // delay queue is full
            // dequeue the oldest entry and write the "left" bank of the RR table
            rr.insert(pc[head],lineaddr[head]);
            INCREMENT(head,DELAYQSIZE);
        }
        lineaddr[tail] = cur_lineaddr;
        pc[tail]=cur_pc;
        cycle[tail] = TRUNCATE(current_core_cycle,TIME_BITS);
        valid[tail] = 1;
        INCREMENT(tail,DELAYQSIZE);
    }

    int dq_ready(uint64_t current_core_cycle)
    {
        // tells whether or not the oldest entry is ready to be dequeued
        if (! valid[head]) {
            // delay queue is empty
            return 0;
        }
        int current_cycle = TRUNCATE(current_core_cycle,TIME_BITS);
        int issuecycle = cycle[head];
        int readycycle = TRUNCATE(issuecycle+DELAY,TIME_BITS);
        if (readycycle >= issuecycle) {
            return (current_cycle < issuecycle) || (current_cycle >= readycycle);
        } else {
            return (current_cycle < issuecycle) && (current_cycle >= readycycle);
        }
    }

    void dq_pop(RecentRequest &rr,uint64_t current_core_cycle)
    {
        // dequeue the entries that are ready to be dequeued,
        // and do a write in the "left" bank of the RR table for each of them
        int i;
        for (i=0; i<DELAYQSIZE; i++) {
            if (!dq_ready(current_core_cycle)) {
                break;
            }
            rr.insert(pc[head],lineaddr[head]);
            valid[head] = 0;
            INCREMENT(head,DELAYQSIZE);
        }
    }

    int lineaddr[DELAYQSIZE]; // RRINDEX+RTAG = 18 bits
    int cycle[DELAYQSIZE];    // TIME_BITS = 12 bits
    int valid[DELAYQSIZE];    // 1 bit
    int pc[DELAYQSIZE];
    int tail;                 // log2 DELAYQSIZE = 4 bits
    int head;                 // log2 DELAYQSIZE = 4 bits
};

//IPtable
struct MetaData{
public:
    MetaData():data(){}

    void insert(int cur_delta)
    {
        // if(cur_delta==0)
        //     return;
        if(data.find(cur_delta)==data.end())
        {
            uint64_t cur_conf=0;
            while(data.size()>=IP_DELTA_SIZE)
            {
                int victim_delta=find_victim();
                // cur_conf=data[victim_delta];
                data.erase(victim_delta);
            }
            data.insert(make_pair(cur_delta,cur_conf));
        }
        increase(cur_delta);
    }

    vector<pair<int,double>> get_info()
    {
        vector<pair<int,double>> res;
        double sum=0;
        if(data.empty())
            return res;
        for(auto i=data.begin();i!=data.end();i++)
        {
            sum+=i->second;
        }
        for(auto i=data.begin();i!=data.end();i++)
        {
            res.push_back(make_pair(i->first,i->second/sum));
        }
        return res;
    }

    void reset()
    {
        data.clear();
    }

private:
    int find_victim()
    {
        uint64_t victim_delta=data.begin()->first;
        for(auto i=data.begin();i!=data.end();i++)
        {
            if(data[victim_delta]>i->second)
            {
                victim_delta=i->first;
            }
        }
        return victim_delta;
    }

    void increase(int delta)
    {
        assert(data.find(delta)!=data.end());
        if(data[delta]>=IP_CONF_MAX)
        {
            for(auto i=data.begin();i!=data.end();i++)
            {
                i->second=((i->second)>>1);
            }
        }
        data[delta]++;
    }

    map<int,uint64_t> data;
};

struct IPTableEntry{

    IPTableEntry():last_page(0),last_offset(0),signature(0),metadata(),repl_metrics(){}

    uint64_t last_page;
    uint64_t last_offset;
    uint64_t signature;
    MetaData metadata;
    ReplMetrics repl_metrics;
};

class IPTable
{
public:
    IPTable():data(IP_TABLE_SET){
        repl=Repl<uint64_t,IPTableEntry>::create_repl(&data,REPL_LRU);
    }

    void train(uint64_t pc,uint64_t addr,SignatureTable &signaturetable)
    {
        uint64_t set_id=TRUNCATE(pc,LOG2_IP_TABLE_SET);
        uint64_t tag=(pc>>LOG2_IP_TABLE_SET);

        if(data[set_id].find(tag)==data[set_id].end())
        {
            while(data[set_id].size()>=IP_TABLE_WAY)
            {
                uint64_t victim_tag=repl->findVictim(set_id);
                data[set_id].erase(victim_tag);
            }
            data[set_id].insert(make_pair(tag,IPTableEntry()));
        }
        uint64_t cur_page=(addr>>(LOG2_PAGE_SIZE-LOG2_BLOCK_SIZE));
        uint64_t cur_offset=TRUNCATE(addr,(LOG2_PAGE_SIZE-LOG2_BLOCK_SIZE));
        cur_page=hash_page(cur_page);
        if(data[set_id][tag].last_page==cur_page)
        {
            int delta=cur_offset-data[set_id][tag].last_offset;
            signaturetable.update(data[set_id][tag].signature,delta);
            data[set_id][tag].signature=update_signature(data[set_id][tag].signature,delta);
        }
        else
        {
            data[set_id][tag].signature=0;
        }
        data[set_id][tag].last_page=cur_page;
        data[set_id][tag].last_offset=cur_offset;
        repl->setEntry(set_id,tag);
    }

    void train(vector<pair<uint64_t,int>>  backs )
    {
        for(auto back:backs)
        {
            uint64_t pc=back.first;
            int64_t delta=back.second;
            uint64_t set_id=TRUNCATE(pc,LOG2_IP_TABLE_SET);
            uint64_t tag=(pc>>LOG2_IP_TABLE_SET);
            if(data[set_id].find(tag)==data[set_id].end())
            {
                while(data[set_id].size()>=IP_TABLE_WAY)
                {
                    uint64_t victim_tag=repl->findVictim(set_id);
                    data[set_id].erase(victim_tag);
                }
                data[set_id].insert(make_pair(tag,IPTableEntry()));
            }
            data[set_id][tag].metadata.insert(delta);
            repl->setEntry(set_id,tag);
        }
    }

    uint64_t get_signature(uint64_t pc)
    {
        uint64_t set_id=TRUNCATE(pc,LOG2_IP_TABLE_SET);
        uint64_t tag=(pc>>LOG2_IP_TABLE_SET);
        if(data[set_id].find(tag)==data[set_id].end())
            return 0;
        repl->setEntry(set_id,tag);
        return data[set_id][tag].signature;
    }

    vector<pair<uint64_t,int>> prefetch(uint64_t pc,uint64_t base_addr,double  fill_l2_threshold,double fill_llc_threshold)
    {
        vector<pair<uint64_t,int>> res;
        uint64_t set_id=TRUNCATE(pc,LOG2_IP_TABLE_SET);
        uint64_t tag=(pc>>LOG2_IP_TABLE_SET);
        if(data[set_id].find(tag)==data[set_id].end())
            return res;
        vector<pair<int,double>> cur_deltas=data[set_id][tag].metadata.get_info();
        sort(cur_deltas.begin(),cur_deltas.end(),[](pair<int,double> i,pair<int,double> j)->bool{return i.second>j.second;});
        if(cur_deltas.empty())
            return res;
        for(auto i=0;i<cur_deltas.size();i++)
        {
            if(cur_deltas[i].first==0)
                continue;
            if(cur_deltas[i].second>=fill_l2_threshold)
            {
                if(SAMEPAGE(base_addr,base_addr+cur_deltas[i].first))
                    res.push_back(make_pair(base_addr+cur_deltas[i].first,FILL_L2));
            }
            else if(cur_deltas[i].second>=fill_llc_threshold)
            {
                if(SAMEPAGE(base_addr,base_addr+cur_deltas[i].first))
                    res.push_back(make_pair(base_addr+cur_deltas[i].first,FILL_LLC));
            }
            else
                break;
        }
        return res;
    }

private:
    uint64_t hash_page(uint64_t page)
    {
        uint64_t temp=page;
        do
        {
            temp=(temp>>PAGE_BITS);
            page=(page^(temp&((1<<PAGE_BITS)-1)));
        }while(temp>0);
        return (page&((1<<PAGE_BITS)-1));
    }

    uint64_t update_signature(uint64_t signature,int delta)
    {
        delta = (delta < 0) ? (((-1) * delta) + (1 << LOG2_BLOCK_SIZE)): delta;
        uint64_t new_signature=bitset<SIGNATURE_BITS>((signature<<LEFT_MOVE_BITS)^delta).to_ullong();
        return new_signature;
    }

    vector<map<uint64_t,IPTableEntry>> data;
    Repl<uint64_t,IPTableEntry> *repl;
};

//LP
vector<uint64_t> trigger_ip_signature(NUM_CPUS,0);
vector<uint64_t> trigger_ip_delay(NUM_CPUS,0);

class LP
{
public:
    void train(uint64_t pc,uint64_t addr,uint8_t cache_hit,uint64_t current_cycle)
    {
        pc=TRUNCATE(pc,PC_WIDTH);
        addr=TRUNCATE(addr,ADDR_WIDTH);
        iptable.train(pc,addr,signaturetable);
        delayqueue.dq_pop(recentrequest,current_cycle);
        iptable.train(recentrequest.train(pc,addr));
        delayqueue.dq_push(pc,addr,current_cycle,recentrequest);
    }

    vector<pair<uint64_t,int>> prefetch(uint32_t cpu,uint64_t pc,uint64_t addr,int degree,double fill_l2_threshold,double fill_llc_threshold)
    {
        pc=TRUNCATE(pc,PC_WIDTH);
        uint64_t signature=iptable.get_signature(pc);
        vector<pair<uint64_t,int>> res;
        vector<pair<uint64_t,int>> same_ip_pf;
        vector<pair<uint64_t,int>> ip_next_pf;
//        if(signature!=0)
//            same_ip_pf=signaturetable.prefetch(signature,addr,degree,fill_l2_threshold,fill_llc_threshold);
        if(!same_ip_pf.empty())
        {
            trigger_ip_signature[cpu]++;
        }
        ip_next_pf =iptable.prefetch(pc,addr,fill_l2_threshold,fill_llc_threshold);
        if(!ip_next_pf.empty())
        {
            trigger_ip_delay[cpu]++;
        }
        set<uint64_t> filter;
        for(auto data:ip_next_pf)
        {
            if(filter.find(data.first)==filter.end())
            {
                res.push_back(data);
                filter.insert(data.first);
            }
        }
        for(auto data:same_ip_pf)
        {
            if(filter.find(data.first)==filter.end())
            {
                res.push_back(data);
                filter.insert(data.first);
            }
        }
        if(res.empty()&&(SAMEPAGE(addr,addr+1)))
            res.push_back(make_pair(addr+1,FILL_LLC));
        sort(res.begin(),res.end(),[](pair<uint64_t,int> i,pair<uint64_t,int> j)->bool{return i.second<j.second;});
        return res;
    }
private:
    SignatureTable signaturetable;
    RecentRequest recentrequest;
    DelayQueue delayqueue;
    IPTable iptable;
};

vector<LP> lp(NUM_CPUS);
vector<FilterTable> ft(NUM_CPUS);
vector<uint64_t> last_pf_fill(NUM_CPUS,0);
vector<uint64_t> last_pf_hit(NUM_CPUS,0);

vector<double> FILL_L2_THRESHOLD(NUM_CPUS,L2_THRESHOLD);
vector<double> FILL_LLC_THRESHOLD(NUM_CPUS,LLC_THRESHOLD);
vector<int> DEGREE(NUM_CPUS,PREFETCH_DEGREE);

void CACHE::l2c_prefetcher_initialize()
{

}

uint32_t CACHE::l2c_prefetcher_operate(uint64_t addr, uint64_t ip, uint8_t cache_hit, uint8_t type, uint32_t metadata_in)
{
    uint64_t base_addr=(addr>>LOG2_BLOCK_SIZE);
    lp[cpu].train(ip,base_addr,cache_hit,current_core_cycle[cpu]);
    if(cache_hit)
    {
        ft[cpu].update(base_addr);
    }
    double hit_rate=0.6;
    if((pf_useful+pf_useless)%256==0)
    {
        uint64_t cur_fill=(pf_useful+pf_useless)-last_pf_fill[cpu];
        if(cur_fill!=0)
        {
            hit_rate=(double)(pf_useful-last_pf_hit[cpu])/(pf_useful+pf_useless-last_pf_fill[cpu]);
        }
        last_pf_fill[cpu]=pf_useful+pf_useless;
        last_pf_hit[cpu]=pf_useful;
    }
#ifdef Dynamic_Adjustment
    if(hit_rate>=L2_THRESHOLD_UP_HIT_RATE)
    {
      FILL_L2_THRESHOLD[cpu]=(FILL_L2_THRESHOLD[cpu]-0.025<=L2_MIN_THRESHOLD)?L2_MIN_THRESHOLD:FILL_L2_THRESHOLD[cpu]-0.025;
    //   FILL_LLC_THRESHOLD[cpu]=(FILL_LLC_THRESHOLD[cpu]-0.025<=LLC_MIN_THRESHOLD)?LLC_MIN_THRESHOLD:FILL_LLC_THRESHOLD[cpu]-0.025;
    }
    else if(hit_rate<=L2_THRESHOLD_DOWN_HIT_RATE)
    {
        FILL_L2_THRESHOLD[cpu]=(FILL_L2_THRESHOLD[cpu]+0.025>=L2_MAX_THRESHOLD)?L2_MAX_THRESHOLD:FILL_L2_THRESHOLD[cpu]+0.025;
        // FILL_LLC_THRESHOLD[cpu]=(FILL_LLC_THRESHOLD[cpu]+0.025>=LLC_MAX_THRESHOLD)?LLC_MAX_THRESHOLD:FILL_LLC_THRESHOLD[cpu]+0.025;
    }
    if(hit_rate>=UP_HIT_RATE)
    {
      DEGREE[cpu]=(DEGREE[cpu]>=PREFETCH_DEGREE_MAX)?PREFETCH_DEGREE_MAX:(DEGREE[cpu]+1);
    //   FILL_LLC_THRESHOLD[cpu]=(FILL_LLC_THRESHOLD[cpu]-0.025<=LLC_MIN_THRESHOLD)?LLC_MIN_THRESHOLD:FILL_LLC_THRESHOLD[cpu]-0.025;
    }
    else if(hit_rate<=DOWN_HIT_RATE)
    {
        DEGREE[cpu]=(DEGREE[cpu]<=PREFETCH_DEGREE_MIN)?PREFETCH_DEGREE_MIN:(DEGREE[cpu]-1);
        // FILL_LLC_THRESHOLD[cpu]=(FILL_LLC_THRESHOLD[cpu]+0.025>=LLC_MAX_THRESHOLD)?LLC_MAX_THRESHOLD:FILL_LLC_THRESHOLD[cpu]+0.025;

    }
#endif
    vector<pair<uint64_t,int>> pf_address=lp[cpu].prefetch(cpu,ip,base_addr,DEGREE[cpu],FILL_L2_THRESHOLD[cpu],FILL_LLC_THRESHOLD[cpu]);
    for(auto i=0;i<pf_address.size();i++)
    {
        if(ft[cpu].insert(pf_address[i].first))
        {
            if(prefetch_line(ip,addr,((pf_address[i].first)<<LOG2_BLOCK_SIZE),pf_address[i].second,0))
            {

            }
            else
            {
                ((CACHE *)lower_level)->cpu=cpu;
                ((CACHE *)lower_level)->prefetch_line(ip,addr,((pf_address[i].first)<<LOG2_BLOCK_SIZE),FILL_LLC,0);
                ((CACHE *)lower_level)->cpu=0;
            }
        }
    }
    return metadata_in;
}

uint32_t CACHE::l2c_prefetcher_cache_fill(uint64_t addr, uint32_t set, uint32_t way, uint8_t prefetch, uint64_t evicted_addr, uint32_t metadata_in)
{
   // stats.prefetcher_cache_fill(addr,set,way,prefetch,evicted_addr);
   // ft[cpu].eviction((evicted_addr>>LOG2_BLOCK_SIZE));
    return metadata_in;
}

//void CACHE::l2c_prefetcher_inform_warmup_complete()
//{
//    stats.prefetcher_inform_warmup_complete();
//    last_pf_fill[cpu]=0;
//    last_pf_hit[cpu]=0;
//    trigger_ip_signature[cpu]=0;
//    trigger_ip_delay[cpu]=0;
//}
//
//void CACHE::l2c_prefetcher_inform_roi_complete()
//{
//    stats.prefetcher_inform_roi_complete();
//}
//
//void CACHE::l2c_prefetcher_roi_stats()
//{
//    stats.prefetcher_roi_stats(cpu,string("L2"));
//    cout<<"trigger ip signature: "<<trigger_ip_signature[cpu]<<endl;
//    cout<<"trigger  ip delay: "<<trigger_ip_delay[cpu]<<endl;
//    cout<<"Prefetch degree: "<< DEGREE[cpu]<<endl;
//    cout<<"Fill L2 threshold: "<<FILL_L2_THRESHOLD[cpu]<<endl;
//    cout<<"Fill LLC threshold: "<<FILL_LLC_THRESHOLD[cpu]<<endl;
//}
//
void CACHE::l2c_prefetcher_final_stats()
{
//
}
