//
// Created by Umasou on 2021/5/28.
//

#ifndef CHAMPSIMTYL_LOG_H
#define CHAMPSIMTYL_LOG_H

#include <fstream>
#include <string>

using namespace std;

class ChampSimLog{
public:
    ChampSimLog(string file_path){
        this->file_path = file_path;
        OsWrite.open(file_path, ofstream::trunc);
        OsWrite.close();
    };
    void makeLog(const string str , const bool is_log)
    {
        if (is_log){
            OsWrite.open(file_path, fstream::app);
            OsWrite<<str;
            OsWrite<<std::endl;
            OsWrite.close();
        }
    }

private:
    ofstream OsWrite;
    string file_path;
};
#endif //CHAMPSIMTYL_LOG_H
