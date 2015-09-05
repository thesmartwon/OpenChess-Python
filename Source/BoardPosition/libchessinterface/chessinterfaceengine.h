
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

#ifndef CHESSINTERFACEENGINE_H_
#define CHESSINTERFACEENGINE_H_

struct chessinterfaceengine {
    mutex* accesslock;
    struct process* p;
    struct chessengineinfo i;
    char* path;
    char* args;
    char* workingDirectory;
    void (*loadedCallback)(struct chessinterfaceengine* engine,
      const struct chessengineinfo* info, void* userdata);
    void (*communicationLogCallback)(struct chessinterfaceengine* engine,
      int outgoing, const char* line, void* userdata);
    void (*quitCallback)(struct chessinterfaceengine* engine,
      void* userdata);
    int readFailure;
    void* userdata;
    int isLoaded;
    int detectionState;
    int closeDownLaunchThread;
    int launchThreadIsRunning;

    // protocol probing options:
    int skipuci;
};

#define DETECTIONSTATE_NONE 0
#define DETECTIONSTATE_PROBING_UCI 1
#define DETECTIONSTATE_PROBING_NOT_UCI 2
#define DETECTIONSTATE_PROBING_WINBOARD_2 3
#define DETECTIONSTATE_PROBING_WINBOARD_2_OPTIONS 4
#define DETECTIONSTATE_PROBING_WINBOARD_1 5

#endif  // CHESSINTERFACEENGINE_H_

