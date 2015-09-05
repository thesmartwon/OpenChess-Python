
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

#ifndef WINDOWS
#if defined(WIN32) || defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(_MSC_VER)
#define WINDOWS
#define _WIN32_WINNT 0x0501
#if defined __MINGW_H
#define _WIN32_IE 0x0400
#endif
#endif
#endif

#include <assert.h>
#include <stdlib.h>
#include <string.h>
#ifdef WINDOWS
#include <process.h>
#include <windows.h>
#else
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#endif

#include "../threading/threading.h"

struct mutex {
#ifdef WINDOWS
    HANDLE m;
#else
    pthread_mutex_t m;
#endif
};

struct semaphore {
#ifdef WINDOWS
    HANDLE s;
#else
    sem_t s;
#endif
};

struct threadinfo {
#ifdef WINDOWS
    HANDLE t;
#else
    pthread_t t;
#endif
};

semaphore* semaphore_Create(int value) {
    semaphore* s = malloc(sizeof(*s));
    if (!s) {
        return NULL;
    }
    memset(s, 0, sizeof(*s));
#ifdef WINDOWS
    s->s = CreateSemaphore(NULL, value, INT_MAX, NULL);
    if (!s->s) {
        free(s);
        return NULL;
    }
#else
    if (sem_init(&s->s, 0, value) != 0) {
        free(s);
        return NULL;
    }
#endif
    return s;
}

void semaphore_Wait(semaphore* s) {
#ifdef WINDOWS
    WaitForSingleObject(s->s, INFINITE);
#else
    sem_wait(&s->s);
#endif
}

void semaphore_Post(semaphore* s) {
#ifdef WINDOWS
    ReleaseSemaphore(s->s, 1, NULL);
#else
    sem_post(&s->s);
#endif
}

void semaphore_Destroy(semaphore* s) {
    if (!s) {return;}
#ifdef WINDOWS
    CloseHandle(s->s);
#else
    sem_destroy(&s->s);
#endif
    free(s);
}

mutex* mutex_Create() {
    mutex* m = malloc(sizeof(*m));
    if (!m) {
        return NULL;
    }
    memset(m, 0, sizeof(*m));
#ifdef WINDOWS
    m->m = CreateMutex(NULL, FALSE, NULL);
    if (!m->m) {
        free(m);
        return NULL;
    }
#else
    pthread_mutexattr_t blub;
    pthread_mutexattr_init(&blub);
#ifndef NDEBUG
    pthread_mutexattr_settype(&blub, PTHREAD_MUTEX_ERRORCHECK);
#else
    pthread_mutexattr_settype(&blub, PTHREAD_MUTEX_NORMAL);
#endif
    while (pthread_mutex_init(&m->m, &blub) != 0) {
        if (errno != EAGAIN) {
            free(m);
            return NULL;
        }
    }
    pthread_mutexattr_destroy(&blub);
#endif
    return m;
}

void mutex_Destroy(mutex* m) {
    if (!m) {return;}
#ifdef WINDOWS
    CloseHandle(m->m);
#else
    while (pthread_mutex_destroy(&m->m) != 0) {
        if (errno != EBUSY) {break;}
    }
#endif
    free(m);
}

void mutex_Lock(mutex* m) {
#ifdef WINDOWS
    WaitForSingleObject(m->m, INFINITE);
#else
    int r = 35;
    while (r == 35) {
        r = pthread_mutex_lock(&m->m);
    }
#ifndef NDEBUG
    assert(r == 0);
#endif
#endif
}

void mutex_Release(mutex* m) {
#ifdef WINDOWS
    ReleaseMutex(m->m);
#else
#ifndef NDEBUG
    assert(pthread_mutex_unlock(&m->m) == 0);
#else
    pthread_mutex_unlock(&m->m);
#endif
#endif
}

threadinfo* thread_CreateInfo() {
    threadinfo* tinfo = malloc(sizeof(*tinfo));
    if (!tinfo) {
        return NULL;
    }
    memset(tinfo, 0, sizeof(*tinfo));
    return tinfo;
}

void thread_FreeInfo(threadinfo* tinfo) {
    if (!tinfo) {return;}
#ifdef WINDOWS
    CloseHandle(tinfo->t);
#else
    pthread_detach(tinfo->t);
#endif
    free(tinfo);
}

struct spawninfo {
    void (*func)(void* userdata);
    void* userdata;
};

#ifdef WINDOWS
static unsigned __stdcall spawnthread(void* data) {
#else
static void* spawnthread(void* data) {
#endif
    struct spawninfo* sinfo = data;
    sinfo->func(sinfo->userdata);
    free(sinfo);
#ifdef WINDOWS
    return 0;
#else
    return NULL;
#endif
}

void thread_Spawn(threadinfo* t, void (*func)(void* userdata), void* userdata) {
    struct spawninfo* sinfo = malloc(sizeof(*sinfo));
    if (!sinfo) {
        return;
    }
    memset(sinfo, 0, sizeof(*sinfo));
    sinfo->func = func;
    sinfo->userdata = userdata;
#ifdef WINDOWS
    HANDLE h = (HANDLE)_beginthreadex(NULL, 0, spawnthread, sinfo, 0, NULL);
    if (t) {
        t->t = h;
    } else {
        CloseHandle(h);
    }
#else
    if (t) {
        while (pthread_create(&t->t, NULL, spawnthread, sinfo) != 0) {
            assert(errno == EAGAIN);
        }
    } else {
        pthread_t thread;
        while (pthread_create(&thread, NULL, spawnthread, sinfo) != 0) {
            assert(errno == EAGAIN);
        }
        pthread_detach(thread);
    }
#endif 
}


