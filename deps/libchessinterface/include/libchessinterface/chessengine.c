
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
#include <unistd.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#ifdef WINDOWS
#include <windows.h>
#endif

#include "protocolexceptions.h"
#include "threading/threading.h"
#include "chessinterface.h"
#include "execproc/execproc.h"
#include "chessinterfaceengine.h"

static int sendline(struct chessinterfaceengine* cie, const char* line, ...) {
    if (!line) {
        return 0;
    }
    char linebuf[1024];
    va_list ap;
    va_start(ap, line);
    vsnprintf(linebuf, sizeof(linebuf), line, ap);
    if (strlen(linebuf) < sizeof(linebuf) - 2) {
#ifdef UNIX
        // some linux engines break when we use \r\n
        strcat(linebuf, "\n");
#else
        // for windows, use \r\n
        strcat(linebuf, "\r\n");
#endif
    }
    void (*communicationLogCallback)(struct chessinterfaceengine* engine,
      int outgoing, const char* line, void* userdata) =
    cie->communicationLogCallback;
    mutex_Release(cie->accesslock);
    if (communicationLogCallback) {
        communicationLogCallback(cie, 1, line, cie->userdata);
    }
    mutex_Lock(cie->accesslock);
    return execproc_Send(cie->p, linebuf);
}

static void freesettingsarray(char** a) {
    while (*a) {
        free(*a);
        a++;
    }
}

static void engineHasQuit(struct chessinterfaceengine* cie) {
    if (!cie->isLoaded) {
        // engine wasn't loaded yet, report loading failure
        struct chessengineinfo* i = &cie->i;
        cie->i.loadError = strdup("Engine shutdown unexpectedly");
        mutex_Release(cie->accesslock);
        void (*loadedCallback)(struct chessinterfaceengine* engine,
          const struct chessengineinfo*, void*) =
        cie->loadedCallback;
        void* userdata = cie->userdata;
        mutex_Release(cie->accesslock);
        if (loadedCallback) {
            loadedCallback(cie, i, userdata);
        }
    } else {
        // engine was already loaded, report quit event
        void (*quitCallback)(struct chessinterfaceengine* engine,
          void*) = cie->quitCallback;
        void* userdata = cie->userdata;
        mutex_Release(cie->accesslock);
        if (quitCallback) {
            quitCallback(cie, userdata);
        }
    }
    mutex_Lock(cie->accesslock);
}

static void readcallback(struct process* p, const char* line,
void* userdata) {
    struct chessinterfaceengine* cie = userdata;
    mutex_Lock(cie->accesslock);
    if (!line) {
        // read failure
        cie->readFailure = 1;
        engineHasQuit(cie);
        mutex_Release(cie->accesslock);
        return;
    }
    void (*communicationLogCallback)(struct chessinterfaceengine* engine,
      int outgoing, const char* line, void* userdata) =
    cie->communicationLogCallback;
    mutex_Release(cie->accesslock);
    if (communicationLogCallback) {
        communicationLogCallback(cie, 0, line, cie->userdata);
    }
    mutex_Lock(cie->accesslock);
    if (!cie->isLoaded &&
    cie->detectionState == DETECTIONSTATE_PROBING_UCI) {
        // positive match for UCI:
        if (strcasecmp(line, "uciok") == 0) {
            cie->isLoaded = 1;
            cie->i.protocolType = strdup("uci");
            int infoCount = 2;
            char** infoArray = malloc(sizeof(char*)*(infoCount*2+1));
            infoArray[infoCount*2] = 0;
            infoArray[0] = strdup("Variants");
            infoArray[1] = strdup("normal");
            infoArray[2] = strdup("SAN");
            infoArray[3] = strdup("0");
            cie->i.engineInfo = (const char* const*)infoArray;
            void (*loadedCallback)(struct chessinterfaceengine* engine,
              const struct chessengineinfo* info, void* userdata) =
            cie->loadedCallback;
            mutex_Release(cie->accesslock);
            if (loadedCallback) {
                loadedCallback(cie, &(cie->i), cie->userdata);
            }
            mutex_Lock(cie->accesslock);
            freesettingsarray(infoArray);
            return;
        }

        // negative match for UCI:
        if (strstr(line, "id ") != line && strstr(line, "option ") != line
        && (strstr(line, "illlegal") || strstr(line, "Illegal")) && strstr(line, "uci")) {
            // engine most likely reports "uci" is not a valid move -> not uci
            cie->detectionState = DETECTIONSTATE_PROBING_NOT_UCI;
        }
    }
    if (!cie->isLoaded &&
    cie->detectionState == DETECTIONSTATE_PROBING_WINBOARD_1) {
        // a move would be a positive match for winboard 1:
        if (strlen(line) >= 4 && line[0] >= 'a' && line[0] <= 'h'
        && line[1] >= '1' && line[1] <= '8') {
            // load as legacy winboard engine
            cie->isLoaded = 1;
            cie->i.protocolType = strdup("cecp1");
            int infoCount = 2;
            char** infoArray = malloc(sizeof(char*)*(infoCount*2+1));
            infoArray[infoCount*2] = 0;
            infoArray[0] = strdup("Variants");
            infoArray[1] = strdup("normal");
            infoArray[2] = strdup("SAN");
            infoArray[3] = strdup("0");
            cie->i.engineInfo = (const char* const*)infoArray;
            void (*loadedCallback)(struct chessinterfaceengine* engine,
              const struct chessengineinfo* info, void* userdata) =
            cie->loadedCallback;
            mutex_Release(cie->accesslock);
            if (loadedCallback) {
                loadedCallback(cie, &(cie->i), cie->userdata);
            }
            mutex_Lock(cie->accesslock);
            freesettingsarray(infoArray);
        }
    }
    if (!cie->isLoaded &&
    cie->detectionState == DETECTIONSTATE_PROBING_WINBOARD_2) {
        // positive match for winboard:
        if (strstr(line, "feature ") == line) {
            cie->detectionState = DETECTIONSTATE_PROBING_WINBOARD_2_OPTIONS;
        }
    }
    if (!cie->isLoaded &&
    cie->detectionState == DETECTIONSTATE_PROBING_WINBOARD_2_OPTIONS) {
        // parse CECPv2 options:
        if (strstr(line, "feature ") == line) {
            if (strstr(line, " done=1")) {
                cie->isLoaded = 1;
                cie->i.protocolType = strdup("cecp2");
                int infoCount = 2;
                char** infoArray = malloc(sizeof(char*)*(infoCount*2+1));
                infoArray[infoCount*2] = 0;
                infoArray[0] = strdup("Variants");
                infoArray[1] = strdup("normal");
                infoArray[2] = strdup("SAN");
                infoArray[3] = strdup("0");
                cie->i.engineInfo = (const char* const*)infoArray;
                void (*loadedCallback)(struct chessinterfaceengine* engine,
                  const struct chessengineinfo* info, void* userdata) =
                cie->loadedCallback;
                mutex_Release(cie->accesslock);
                if (loadedCallback) {
                    loadedCallback(cie, &(cie->i), cie->userdata);
                }
                mutex_Lock(cie->accesslock);
                freesettingsarray(infoArray);
                return;
            }
        }
    }
    mutex_Release(cie->accesslock);
}

static int checklaunchshutdown(struct chessinterfaceengine* cie) {
    mutex_Lock(cie->accesslock);
    if (cie->closeDownLaunchThread) {
        cie->launchThreadIsRunning = 0;
        mutex_Release(cie->accesslock);
        return 1;
    }
    mutex_Release(cie->accesslock);
    return 0;
}

// This function will run in the thread that launches the engine:
static void chessinterfacelaunchthread(void* userdata) {
    struct chessinterfaceengine* cie = userdata;

    // protocol exceptions:
    protocolexceptions_SetByBinName(cie, cie->path);

    // launch process:
    int i = execproc_Run(cie->path, cie->args,
    cie->workingDirectory, &(cie->p));
    memset(&(cie->i), 0, sizeof(cie->i));
    void (*loadedCallback)(struct chessinterfaceengine* engine,
      const struct chessengineinfo* info, void* userdata) =
    cie->loadedCallback;
    if (i != 0) {
        switch (i) {
        case EXECPROC_ERROR_NOSUCHFILE:
            cie->i.loadError = strdup("No such file");
            break;
        case EXECPROC_ERROR_CANNOTOPENFILE:
            cie->i.loadError = strdup("Cannot open file");
            break;
        case EXECPROC_ERROR_CANNOTRUNFILE:
            cie->i.loadError = strdup("Cannot run file");
            break;
        default:
            cie->i.loadError = strdup("Unknown error");
        }
        cie->launchThreadIsRunning = 0;
        loadedCallback(cie, &(cie->i), cie->userdata);
        return;
    }

    // launch read thread:
    execproc_Read(cie->p, readcallback, cie);  // run engine

    // allow engine to start:
#ifdef UNIX
    usleep(100 * 1000);
#else
    Sleep(100);
#endif

    if (checklaunchshutdown(cie)) {return;}

    // probe for UCI:
    mutex_Lock(cie->accesslock);
    int detectuci = 1;
    if (cie->skipuci) {
        detectuci = 0;
    }
    if (detectuci) {
        cie->detectionState = DETECTIONSTATE_PROBING_UCI;
        if (!sendline(cie, "uci")) {
            cie->launchThreadIsRunning = 0;
            cie->i.loadError = strdup("Cannot send data to engine");
            mutex_Release(cie->accesslock);
            loadedCallback(cie, &(cie->i), cie->userdata);
            return;
        }
    }
    mutex_Release(cie->accesslock);

    if (checklaunchshutdown(cie)) {return;}

    // wait a maximum of 3 seconds for UCI probing:
    int isuci = 0;
    if (detectuci) {
        i = 30;
        while (i > 0) {
#ifdef UNIX
            usleep(100 * 1000);
#else
            Sleep(100);
#endif
            mutex_Lock(cie->accesslock);
            if (cie->isLoaded) {
                isuci = 1;
                break;
            }
            if (cie->detectionState == DETECTIONSTATE_PROBING_NOT_UCI) {
                break;
            }
            if (i > 1) {
                mutex_Release(cie->accesslock);
                if (checklaunchshutdown(cie)) {return;}
            }
            i--;
        }
    }

    // if not UCI, probe for winboard:
    if (!isuci) {
        cie->detectionState = DETECTIONSTATE_PROBING_WINBOARD_2;
        if (!sendline(cie, "xboard\nprotover 2")) {
            cie->launchThreadIsRunning = 0;
            cie->i.loadError = strdup("Cannot send data to engine");
            mutex_Release(cie->accesslock);
            loadedCallback(cie, &(cie->i), cie->userdata);
            return;
        }
        mutex_Release(cie->accesslock);

        // wait a maximum of 3 seconds for winboard 2 probing:
        i = 30;
        int iscecp2 = 0;
        while (i > 0) {
#ifdef UNIX
            usleep(100 * 1000);
#else
            Sleep(100);
#endif
            mutex_Lock(cie->accesslock);
            if (cie->isLoaded || cie->detectionState !=
            DETECTIONSTATE_PROBING_WINBOARD_2) {
                iscecp2 = 1;
                break;
            }
            if (i > 1) {
                mutex_Release(cie->accesslock);
                if (checklaunchshutdown(cie)) {return;}
            }
            i--;
        }
        if (!iscecp2) {
            // ensure this is a CECP1 engine by triggering a move
            cie->detectionState = DETECTIONSTATE_PROBING_WINBOARD_1;
            if (!sendline(cie, "new\ntime 1\ngo\n?")) {
                cie->launchThreadIsRunning = 0;
                cie->i.loadError = strdup("Cannot send data to engine");
                mutex_Release(cie->accesslock);
                loadedCallback(cie, &(cie->i), cie->userdata);
                return;
            }

            // wait a maximum of 3 seconds for the winboard 1 move:
            i = 30;
            int iscecp1 = 0;
            while (i > 0) {
#ifdef UNIX
                usleep(100 * 1000);
#else
                Sleep(100);
#endif
                mutex_Lock(cie->accesslock);
                if (cie->isLoaded || cie->detectionState !=
                DETECTIONSTATE_PROBING_WINBOARD_1) {
                    iscecp1 = 1;
                    break;
                }
                if (i > 1) {
                    mutex_Release(cie->accesslock);
                    if (checklaunchshutdown(cie)) {return;}
                }
                i--;
            }

            if (!iscecp1) {
                // this is not a chess engine as it seems.
                cie->launchThreadIsRunning = 0;
                cie->i.loadError = strdup("Not a chess engine");
                mutex_Release(cie->accesslock);
                loadedCallback(cie, &(cie->i), cie->userdata);
                return;
            }
        }
    }
    cie->launchThreadIsRunning = 0; 
    mutex_Release(cie->accesslock);
}

struct chessinterfaceengine* chessinterface_Open(const char* path,
const char* args, const char* workingDirectory,
const char* const* protocolOptions,
void (*engineLoadedCallback)(struct chessinterfaceengine* engine,
  const struct chessengineinfo* info, void* userdata),
void (*engineErrorCallback)(struct chessinterfaceengine* engine,
  const char* error, void* userdata),
void (*engineTalkCallback)(struct chessinterfaceengine* engine,
  const char* talk, void* userdata),
void (*engineCommunicationLogCallback)(struct chessinterfaceengine* engine,
  int outgoing, const char* line, void* userdata),
void (*engineQuitCallback)(struct chessinterfaceengine* engine,
  void* userdata),
void* userdata) {
    struct chessinterfaceengine* cie = malloc(sizeof(*cie));
    if (!cie) {return NULL;}
    memset(cie, 0, sizeof(*cie));
    cie->accesslock = mutex_Create();
    if (!cie->accesslock) {
        free(cie);
        return NULL;
    }
    cie->path = strdup(path);
    if (!cie->path) {
        mutex_Destroy(cie->accesslock);
        free(cie);
        return NULL;
    }
    cie->launchThreadIsRunning = 1;
    cie->userdata = userdata;
    cie->loadedCallback = engineLoadedCallback;
    cie->communicationLogCallback = engineCommunicationLogCallback;
    cie->quitCallback = engineQuitCallback;
    if (args) {
        cie->args = strdup(args);
    }
    if (workingDirectory) {
        cie->workingDirectory = strdup(workingDirectory);
    }

    thread_Spawn(NULL, chessinterfacelaunchthread, cie);
    return cie;
}

static void chessinterface_CloseThread(void* d) {
    // this completes the closedown process in a separate thread
    // to do it in parallel

    struct chessinterfaceengine* cie = d;

    // instruct launch thread to close down if running:
    mutex_Lock(cie->accesslock);
    if (cie->launchThreadIsRunning) {
        cie->closeDownLaunchThread = 1;
        mutex_Release(cie->accesslock);
        
        // wait for launch thread to terminate:
        while (1) {
            mutex_Lock(cie->accesslock);
            if (!cie->launchThreadIsRunning) {
                break;
            }
            mutex_Release(cie->accesslock);
#ifdef UNIX
            usleep(500 * 1000);
#else
            Sleep(500);
#endif
        }
    }

    // by now, no read callbacks or launch thread
    // should be running.

    // quit event:
    if (!cie->readFailure) {
        engineHasQuit(cie);
    }

    // free things:
    mutex_Release(cie->accesslock);
    free(cie->args);
    free(cie->workingDirectory);
    free(cie->path);
}

void chessinterface_Close(struct chessinterfaceengine* cie) {
    mutex_Lock(cie->accesslock);
    struct process* p = cie->p;
    cie->detectionState = DETECTIONSTATE_NONE;
    mutex_Release(cie->accesslock);

    // close down read callbacks:
    execproc_Close(cie->p);
    mutex_Lock(cie->accesslock);

    // do remaining things asynchronously because shutting down
    // the launch thread might not be instant:
    thread_Spawn(NULL, &chessinterface_CloseThread, cie);
}

