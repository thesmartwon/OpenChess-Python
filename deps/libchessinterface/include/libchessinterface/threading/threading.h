
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

// Threading code

#ifndef THREADING_THREADING_H_
#define THREADING_THREADING_H_

#ifndef WINDOWS
#if defined(WIN32) || defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(_MSC_VER)
#define WINDOWS
#ifdef _WIN32_WINNT
#undef _WIN32_WINNT
#endif
#define _WIN32_WINNT 0x0501
#if defined __MINGW_H
#define _WIN32_IE 0x0400
#endif
#endif
#endif

typedef struct mutex mutex;
typedef struct threadinfo threadinfo;
typedef struct semaphore semaphore;

// create, destroy a mutex:
mutex* mutex_Create();
void mutex_Destroy(mutex* m);

// lock and release a mutex:
void mutex_Lock(mutex* m);
void mutex_Release(mutex* m);

// create, destroy a semaphore:
semaphore* semaphore_Create(int value);  // init with given value
void semaphore_Destroy(semaphore* s);

// wait for a semaphore (decrementing it), and post (increment it again)
void semaphore_Wait(semaphore* s);
void semaphore_Post(semaphore* s);

// create threadinfo:
threadinfo* thread_CreateInfo();

// spawn a new thread:
void thread_Spawn(threadinfo* tinfo, void (*func)(void* userdata),
void* userdata); 

// free threadinfo (you can safely do this when the thread is still running):
void thread_FreeInfo(threadinfo* tinfo);

#endif  // THREADING_THREADING_H_

