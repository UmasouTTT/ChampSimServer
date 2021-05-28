//
// Created by Umasou on 2021/5/25.
//

#ifndef CHAMPSIM_UTIL_H
#define CHAMPSIM_UTIL_H

#include <fstream>
#include <string>

class Tool{
public:
    Tool(void);
    virtual ~Tool(void);

    static void log(const std::string & file_string, const std::string str , const bool is_log)
    {
        if (is_log){
            std::ofstream	OsWrite(file_string,std::ofstream::app);
            OsWrite<<str;
            OsWrite<<std::endl;
            OsWrite.close();
        }
    }
};

#endif //CHAMPSIM_UTIL_H
