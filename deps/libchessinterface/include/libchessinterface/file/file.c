
// libchessinterface, a library to run chess engines
// Copyright (C) 2012  Jonas Thiem
//
// libchessinterface is free software: you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of
// the License, or (at your option) any later version.
//
// libchessinterface is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with libchessinterface in a file named COPYING.txt.
// If not, see <http://www.gnu.org/licenses/>.


#include "os/os.h"
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>

#ifdef WINDOWS
#include <windows.h>
#include "shlwapi.h"
#else
#include <limits.h>
#include <sys/stat.h>
#endif

#include "file/file.h"

static char file_NativeSlash() {
#ifdef WINDOWS
        return '\\';
#else
        return '/';
#endif
}

static int file_IsDirectorySeparator(char c) {
#ifdef WINDOWS
    if (c == '/' || c == '\\') {
        return 1;
    }
#else
    if (file_NativeSlash() == c) {
        return 1;
    }
#endif
    return 0;
}

void file_MakeSlashesNative(char* path) {
    unsigned int i = 0;
    while (i < strlen(path)) {
        if (file_IsDirectorySeparator(path[i])) {
            path[i] = file_NativeSlash();
        }
        i++;
    }
}

int file_Cwd(const char* path) {
    while (path[0] == '.' && strlen(path) > 1 && file_IsDirectorySeparator(path[1])) {
        path += 2;
    }
    if (strcasecmp(path, "") == 0 || strcasecmp(path, ".") == 0) {
        return 1;
    }
    char* pathcopy = strdup(path);
    if (!pathcopy) {
        return 0;
    }
    file_MakeSlashesNative(pathcopy);
#ifdef WINDOWS
    if (SetCurrentDirectory(pathcopy) == 0) {
        free(pathcopy);
        return 0;
    }
#else
    if (chdir(pathcopy) != 0) {
        free(pathcopy);
        return 0;
    }
#endif
    free(pathcopy);
    return 1;
}

char* file_GetCwd() {
    char cwdbuf[2048] = "";
#ifdef WINDOWS
    if (GetCurrentDirectory(sizeof(cwdbuf), cwdbuf) <= 0) {
        return 0;
    }
    // turn all paths like C:\blubb\ into C:/blubb/ (blitwizard-style paths)
    unsigned int i = 0;
    while (i <= strlen(cwdbuf)) {
        if (cwdbuf[i] == '\\') {
            cwdbuf[i] = '/';
        }
        i++;
    }
#else
    if (!getcwd(cwdbuf, sizeof(cwdbuf))) {
        return 0;
    }
#endif
    return strdup(cwdbuf);
}

int file_IsDirectory(const char* path) {
#ifndef WINDOWS
    struct stat info;
    int r = stat(path,&info);
    if (r < 0) {
        return 0;
    }
    if (S_ISDIR(info.st_mode) != 0) {
        return 1;
    }
    return 0;
#endif
#ifdef WINDOWS
    if (PathIsDirectory(path) != FALSE) {
        return 1;
    }
    return 0;
#endif
}

int file_DoesFileExist(const char* path) {
#ifndef WINDOWS
        struct stat st;
        if (stat(path,&st) == 0) {
            return 1;
        }
        return 0;
#else
        DWORD fileAttr;
        fileAttr = GetFileAttributes(path);
        if (0xFFFFFFFF == fileAttr) {
            return 0;
        }
        return 1;
#endif
}


static int file_LatestSlash(const char* path) {
    int i = strlen(path)-1;
    while (!file_IsDirectorySeparator(path[i]) && i > 0) {
        i--;
    }
    if (i <= 0) {
        i = -1;
    }
    return i;
}

static void file_CutOffOneElement(char* path) {
    while (1) {
        int i = file_LatestSlash(path);
        // check if there is nothing left to cut off for absolute paths
#ifdef WINDOWS
        if (i == 2 && path[1] == ':' && (tolower(path[0]) >= 'a' && tolower(path[0]) <= 'z')) {
            return;
        }
#else
        if (i == 0) {
            return;
        }
#endif
        // see what we can cut off
        if (i < 0) {
            // just one relative item left -> empty to current dir ""
            path[0] = 0;
            return;
        }else{
            if (i == (int)strlen(path)-1) {
                // slash is at the end (directory path).
                path[i] = 0;
                if (strlen(path) > 0) {
                    if (path[strlen(path)-1] == '.') {
                        // was this a trailing ./ or ../?
                        if (strlen(path) > 1) {
                            if (path[strlen(path)-2] == '.') {
                                // this is ../, so we're done when the .. is gone
                                path[strlen(path)-2] = 0;
                                return;
                            }
                        }
                        // it is just ./ so we need to carry on after removing it
                        path[strlen(path)-1] = 0;
                    }
                }
            }else{
                path[i+1] = 0;
                return;
            }
        }
    }
}

char* file_AddComponentToPath(const char* path, const char* component) {
    int addslash = 0;
    if (strlen(path) > 0) {
        if (!file_IsDirectorySeparator(path[strlen(path)-1])) {
            addslash = 1;
        }
    }
    char* newpath = malloc(strlen(path)+addslash+1+strlen(component));
    if (!newpath) {
        return NULL;
    }
    memcpy(newpath, path, strlen(path));
    if (addslash) {
        newpath[strlen(path)] = file_NativeSlash();
    }
    memcpy(newpath + strlen(path) + addslash, component, strlen(component));
    newpath[strlen(path) + addslash + strlen(component)] = 0;
    return newpath;
}

void file_StripComponentFromPath(char* path) {
    file_MakeSlashesNative(path);

    int repeat = 1;
    while (repeat) {
        repeat = 0;
        if (strlen(path) > 0) {
            unsigned int slashpos = file_LatestSlash(path);
            if (slashpos > 0) {
                if (slashpos >= strlen(path)-1) {
                    repeat = 1;
                }
                path[slashpos] = 0;
            }else{
                path[0] = 0;
            }
        }
    }
}

char* file_GetAbsolutePathFromRelativePath(const char* path) {
    // cancel for absolute paths
    if (!file_IsPathRelative(path)) {
        return strdup(path);
    }

    // cut off unrequired clutter
    while (path[0] == '.' && path[1] == file_NativeSlash()) {
        path += 2;
    }

    // get current working directory
    char* currentdir = file_GetCwd();
    if (!currentdir) {
        return NULL;
    }

    // process ../
    while (path[0] == '.' && path[1] == '.' && path[2] == file_NativeSlash()) {
        file_CutOffOneElement(currentdir);
        path += 3;
    }

    // allocate space for new path
    char* newdir = malloc(strlen(currentdir) + 1 + strlen(path) + 1);
    if (!newdir) {
        free(currentdir);
        return NULL;
    }

    // assemble new path
    memcpy(newdir, currentdir, strlen(currentdir));
    char slash = file_NativeSlash();
    newdir[strlen(currentdir)] = slash;
    memcpy(newdir + strlen(currentdir) + 1, path, strlen(path));
    newdir[strlen(currentdir) + 1 + strlen(path)] = 0;

    free(currentdir);
    return newdir;
}

char* file_GetDirectoryPathFromFilePath(const char* path) {
    if (file_IsDirectory(path)) {
        return strdup(path);
    }else{
        char* pathcopy = strdup(path);
        if (!pathcopy) {
            return NULL;
        }
        int i = file_LatestSlash(path);
        if (i < 0) {
            free(pathcopy);
            return strdup("");
        }else{
            pathcopy[i+1] = 0;
            return pathcopy;
        }
    }
}

int file_IsPathRelative(const char* path) {
#ifdef WINDOWS
    if (PathIsRelative(path) == TRUE) {
        return 1;
    }
    return 0;
#else
    if (file_IsDirectorySeparator(path[0])) {
        return 0;
    }
    return 1;
#endif
}

char* file_GetAbsoluteDirectoryPathFromFilePath(const char* path) {
    char* p = file_GetDirectoryPathFromFilePath(path);
    if (!p) {
        return NULL;
    }

    if (!file_IsPathRelative(p)) {
        return p;
    }

    char* p2 = file_GetAbsolutePathFromRelativePath(p);
    if (!p2) {
        return NULL;
    }
    return p2;
}

char* file_GetFileNameFromFilePath(const char* path) {
    int i = file_LatestSlash(path);
    if (i < 0) {
        return strdup(path);
    }else{
        char* filename = malloc(strlen(path)-i+1);
        if (!filename) {
            return NULL;
        }
        memcpy(filename, path + i + 1, strlen(path)-i);
        filename[strlen(path)-i] = 0;
        return filename;
    }
}

int file_ContentToBuffer(const char* path, char** buf, size_t* buflen) {
    FILE* r = fopen(path, "rb");
    if (!r) {
        return 0;
    }
    // obtain file size
    fseek(r, 0L, SEEK_END);
    unsigned int size = ftell(r);
    fseek(r, 0L, SEEK_SET);
    // allocate buf
    char* fbuf = malloc(size+1);
    if (!fbuf) {
        fclose(r);
        return 0;
    }
    // read data
    int i = fread(fbuf, 1, size, r);
    fclose(r);
    // check data
    if (i != (int)size) {
        free(fbuf);
        return 0;
    }
    *buflen = size;
    *buf = fbuf;
    return 1;
}

char* file_GetTempPath(const char* name) {
#ifdef WINDOWS
    return NULL;
#else
    char* tmppath = malloc(strlen("/tmp/") + 1 + strlen(name));
    if (!tmppath) {
        return NULL;
    }
    memcpy(tmppath, "/tmp/", strlen("/tmp/"));
    memcpy(tmppath + strlen("/tmp/"), name, strlen(name));
    tmppath[strlen("/tmp/") + strlen(name)] = 0;
    return tmppath;
#endif
}

#ifdef WINDOWS
#include <shlobj.h>
char* file_GetUserFileDir() {
    char programsdirbuf[MAX_PATH+1];
    SHGetFolderPath(NULL, CSIDL_PERSONAL, NULL, 0, programsdirbuf);
    programsdirbuf[MAX_PATH] = 0;
    return strdup(programsdirbuf);
}
#else
char* filesystem_GetUserFileDir() {
    char programsdirbuf[300];
    strncpy(programsdirbuf, getenv("HOME"), 299);
    programsdirbuf[299] = 0;
    return strdup(programsdirbuf);
}
#endif

