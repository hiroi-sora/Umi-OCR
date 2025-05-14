//=====================================================================
//
// PyStand.h -
//
// Created by skywind on 2022/02/03
// Last Modified: 2022/02/03 23:39:52
//
//=====================================================================
#ifndef _PYSTAND_H_
#define _PYSTAND_H_

#include <stdio.h>
#include <windows.h>
#include <shlwapi.h>
#include <string>
#include <vector>

//---------------------------------------------------------------------
// PyStand
//---------------------------------------------------------------------
class PyStand
{
public:
    virtual ~PyStand();
    PyStand(const wchar_t *runtime);
    PyStand(const char *runtime);

public:
    std::wstring Ansi2Unicode(const char *text);

    int RunString();

    int DetectScript();

protected:
    bool CheckEnviron(const wchar_t *rtp);
    bool LoadPython();

protected:
    typedef int (*t_Py_Main)(int argc, wchar_t **argv);
    t_Py_Main _Py_Main;

protected:
    HINSTANCE _hDLL;
    std::wstring _cwd;     // current working directory
    std::wstring _args;    // arguments
    std::wstring _pystand; // absolute path of pystand
    std::wstring _runtime; // absolute path of embedded python runtime
    std::wstring _home;    // home directory of PyStand.exe
    std::wstring _script;  // init script like PyStand.int or PyStand.py
    std::vector<std::wstring> _argv;
    std::vector<std::wstring> _py_argv;
    std::vector<wchar_t *> _py_args;
};

#endif
