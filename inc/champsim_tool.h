//
// Created by Umasou on 2021/5/25.
//

#ifndef CHAMPSIM_UTIL_H
#define CHAMPSIM_UTIL_H

#include <fstream>
#include <string>
#include <sstream>

class Tool{
public:
    Tool(void);
    virtual ~Tool(void);

    static float calculate_prefetch_accuracy(uint64_t old_pf_useful, uint64_t new_pf_useful, uint64_t old_pf_issued, uint64_t new_pf_issued){
        float temp_useful = new_pf_useful - old_pf_useful;
        float temp_issued = new_pf_issued - old_pf_issued;
        return temp_useful / temp_issued;
    }

    static string float_2_string(float value){
        ostringstream out;
        out << value;
        string result = out.str();
        return result;
    }
};

#endif //CHAMPSIM_UTIL_H
