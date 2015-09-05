
// This is an example using libchessinterface.
// It opens a chess engine and then shows a few details on it.

// Install the library first.
// Then compile like this:
//   gcc -o ./example example.c -lchessinterface

// Detect windows:
#ifndef WINDOWS
#if defined(WIN32) || defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(_MSC_VER)
#define WINDOWS
#endif
#endif

// A few includes:
#include <string.h>
#include <stdio.h>
#include "chessinterface.h"
#ifdef WINDOWS
#define strdup _strdup
#include <windows.h>
#endif

// Set to 1 when engine was loaded and probed:
static volatile int probed = 0;

// engine loaded callback which will be called when
// it has been loaded:
static void engineLoadedCallback(struct chessinterfaceengine* engine,
const struct chessengineinfo* info,
void* userdata) {
    // first, handle load errors properly:
    if (info->loadError) {
        printf("Failed to load engine.\n");
#ifdef WINDOWS
        MessageBox(NULL, "Failed to load engine.", "Load Error",
        MB_ICONERROR|MB_OK);
#endif

        // tell main thread we're done:
        probed = 1;
        return;
    }
    
    // compose some nice info output:
    char output[256] = "";
    char line[64];

    // first, add engine protocol name to output:
    snprintf(line, sizeof(line),
    "Engine protocol: %s\n", info->protocolType);
    line[sizeof(line)-1] = 0;
    strncat(output, line, sizeof(output)-strlen(output)-1);

    // then add detailed engine info values:
    const char* const* p = info->engineInfo;
    while (*p) {
        snprintf(line, sizeof(line),
        "Engine info value: %s: %s\n", *p, *(p+1));
        line[sizeof(line)-1] = 0;
        strncat(output, line, sizeof(output)-strlen(output)-1);
        p += 2;
    }

    // show output:
    printf("%s", output);
#ifdef WINDOWS
    MessageBox(NULL, output, "Engine Detection Results",
    MB_ICONINFORMATION|MB_OK);
#endif

    chessinterface_Close(engine);

    // tell main thread we're done:
    probed = 1;
}

static void engineCommunicationLogCallback(
struct chessinterfaceengine* engine, int outgoing, const char* line,
void* userdata) {
    // display communication:
    printf("Communication (%d): %s\n", outgoing, line);
}

int main(int argc, const char** argv) {
    char* engine;
    if (argc < 2) {
#ifndef WINDOWS
        // On Unix, require command line parameter:
        printf("Please specify an engine to probe.\n");
        return 1;
#else
        // On Windows, show a file open dialog:
        OPENFILENAME dialog;
        char fname[260] = "";
        memset(&dialog, 0, sizeof(dialog));
        dialog.lStructSize = sizeof(dialog);
        dialog.lpstrFile = fname;
        dialog.nMaxFile = sizeof(fname);
        dialog.lpstrFilter = "Chess engine program\0*.EXE\0";
        dialog.nFilterIndex = 1;
        dialog.lpstrFileTitle = "Open chess engine for inspection";
        dialog.nMaxFileTitle = 0;
        dialog.lpstrInitialDir = NULL;
        dialog.Flags = OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;
        if (GetOpenFileName(&dialog) == TRUE) {
            engine = strdup(fname);
        } else {
            return 1;
        }
#endif
    } else {
        // engine was passed as cmd arg
        engine = strdup(argv[1]);
    }

    // open chess engine for detection:
    struct chessinterfaceengine* e = chessinterface_Open(
        engine, "",
        NULL, NULL,
        &engineLoadedCallback,
        NULL,
        NULL,
        &engineCommunicationLogCallback,
        NULL,
        NULL
    );

    while (!probed) {
        // wait until engine is probed
#ifdef WINDOWS
        Sleep(50);
#else
        usleep(50000);
#endif
    }
    return 0;
}

