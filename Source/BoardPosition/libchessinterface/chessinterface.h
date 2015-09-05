
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

#ifndef CHESSINTERFACE_H_
#define CHESSINTERFACE_H_

// WELCOME! :-)
//
// Hello fellow programmer!
// This is an interface for launching chess engines.
// This header file is also a reference documentation.
//
// Please don't be overwhelmed by the amount of information,
// and consider starting by reading example.c first to get a rough
// idea how practical usage might look like.


// Represents a launched engine:
struct chessinterfaceengine;

// This struct contains retrieved information about a launched engine:
struct chessengineinfo {
    // possible loading problems:
    const char* loadError;  // if not NULL, the engine failed to load!

    // the following options only have proper values if loadError is NULL:
    const char* protocolType;  // "cecp1", "cecp2", "uci"
    const char* const* engineInfo;
      // A null-terminated list of info name/value pairs.
      // May be NULL if loadError is specified/not NULL.
      // Supported values (not necessarily all present/in that order):
      // {
      //   "SAN",
      //    "1", // the engine sends moves and thinking output as SAN,
      //         // and also *expects YOU* to use SAN for moves you pass
      //         // to it.
      //   "HashTableSizeSupported",
      //    "1", // it appears the engine has understood and obeys
      //         // the HashTableSize protocol option. "0" if not.
      //   "PonderSupported",
      //    "1", // it appears the engine understands the Ponder protocol
      //         // option (otherwise: "0")
      //   "CoresSupported",
      //    "1", // it appears the engine understands the Cores option (or "0")
      //   "Variants",
      //   "normal,suicide,xiangqi,..",  // comma separated list of variants
      //   NULL  // last entry is always NULL
      // }
      // Important: the "..Supported" info may be wrong when passing
      // you "1"/indicating support, since CECPv2 engines might not
      // openly reject options they ignored/didn't understand
      // (although most of them should).
};

// Get minor and major version number of the library:
int chessinterface_GetMinorLibVersion();  // The X in 1.x (5 in v1.5)
int chessinterface_GetMajorLibVersion();  // The X in X.5 (1 in v1.5)

// Open a chess engine from the given binary path.
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
void* userdata);
// Return value: a chess interface engine struct pointer.
// args:
//   command line arguments, e.g. "-hashSize 2048 -uci", or ""/NULL
// workingDirectory:
//   the working directory for the engine, or NULL for current
// protocolOptions:
//   NULL for no protocol options, otherwise an array of option
//   name strings followed by value strings, and finally a NULL
//   entry, e.g. { "option1", "value1", "option2", "value2", NULL }
//   Protocol options are generic options supported through the
//   protocol for most engines (unlike specific the engine options),
//   or other protocol details you might want to specify.
//   Possible protocol options:
//      "AllowSAN"        "1": You support the SAN move notation as
//                        used in PGN, and the engine may use it.
//                        Default: "0"
//      "HashTableSize"   Specify hash table size for the engine
//                        in mb, e.g. "256".
//                        Winboard engines will use this as total
//                        memory limit.
//      "Ponder"          Specify whether pondering (thinking on
//                        the opponent's time) is enabled ("1")
//                        or not ("0").
//      "Cores"           Specify the amount of search threads
//                        (which should equal cpu cores) to use.
//      "ForceProtocol"   Don't auto-detect protocol but force the
//                        specific protocol. Possible values:
//                        "cecp1"/"cecp2"/"uci".
// engineLoadedCallback:
//   This function will be called FROM ANOTHER THREAD as soon as
//   the engine has been initialised and is believed to be ready
//   for use without much further delay.
//   You will be supplied with the engine info, which contains
//   e.g. the detected protocol.
// engineErrorCallback:
//   Some engines support reporting internal errors as readable
//   string. If you provide this function (not NULL), it will be
//   called with the error info FROM ANOTHER THREAD.
// engineTalkCallback:
//   Some engine support talking with the user. When you use
//   chessinterface_Usertalk(), the engine can possibly respond
//   through this callback if you provide it (not NULL), again
//   FROM ANOTHER THREAD.
// engineCommunicationLogCallback:
//   If you provide this function (not NULL), it will be called for
//   every line sent to (outgoing = 1) or received from (outgoing = 0)
//   the engine. This may be useful to an engine programmer who
//   wishes to debug their engine using your GUI.
// engineQuitCallback:
//   If the engineLoadedCallback has already been called with success
//   (no loadError), the engine will be up and running, but at some
//   point it might obviously quit. In that case, this callback will
//   be called if provided.
// userdata:
//   This userdata will be provided to all of your callbacks.

// Instruct the engine to start a new game:
void chessinterface_StartGame(struct chessinterfaceengine* engine,
int playingWhite, int analyze,
const char* variant,
void (*thinkCallback)(int score, int nodes, const char* pv, void* userdata),
void (*resignCallback)(void* userdata),
void (*drawCallback)(void* userdata),
void* userdata);
// playingWhite:
//   1: engine plays white, 0: engine plays black
// analyze:
//   1: engine shouldn't play but only analyze, 0: engine plays
// variant:
//   Specify the variant you wish to play, e.g. "normal" for standard
//   FIDE chess, or another for another variant.
//   Some variants need another move format!
//   Consult http://www.open-aurec.com/wbforum/WinBoard/engine-intf.html
//   for possible variants and how moves are notated for them.
// thinkCallback:
//   This function, if not NULL, will be called when the engine
//   emits thinking lines with score, the node count searched so far
//   and the principal variation. Additionally, you get passed your
//   own userdata.
// resignCallback:
//   In a regular game (not analyze mode), the engine might want to
//   resign. If it does so, this callback will be called.
// drawCallback:
//   In a regular game (not analyze mode), the engine might offer
//   a draw. If that happens you should ask the human player whether
//   they want to accept the draw, and if they do, use
//   chessinterface_Result to end the game with 1/2-1/2.
//   If you want the human to offer a draw to the engine, use
//   chessinterface_Userdraw().
// userdata:
//   This userdata will be given to your callbacks.
// If the engine plays white, you need to use chessinterface_Go
// to make it play. Otherwise, it will simply respond to each
// chessinterface_Move.
// Important: this command resets the board! To start a game form
// a non-standard position, use chessinterface_SetFEN right afterwards.
// All callbacks will be called FROM ANOTHER THREAD.

// Set the time control of the current game:
void chessinterface_SetTimeControl(struct chessinterfaceengine* engine,
int timeInSeconds, int movesUntilIncrease, int increasePerMoveSeconds);
// timeInSeconds: total time slice in seconds
// movesUntilIncrease: full moves after which time slice will be granted
//   again, e.g. 40 for every 40 moves (or 0 for never)
// increasePerMoveSeconds: seconds that will be added per move (or 0).
// After calling this once at the beginning of a game,
// use chessinterface_UpdateClockTime to keep the engine informed
// of the clock time.

// Calculate initial move as current color:
void chessinterface_Go(struct chessinterfaceengine* engine,
int (*movecallback)(const char* move, void* userdata), void* userdata);
// The provided callback function will be called FROM ANOTHER THREAD
// as soon as the engine finished calculating the move,
// with the move and your provided userdata as parameters.
// Your move callback should return 1 if the move was valid and accepted,
// or 0 if it was invalid.

// Pass user talk to the engine:
void chessinterface_Usertalk(struct chessinterfaceengine* engine,
const char* talk);
// Please note the vast majority of engines will probably not
// respond. However, I personally know of a chess engine with
// chat functionality :)

// Pass a move done by the user to the engine:
void chessinterface_Usermove(struct chessinterfaceengine* engine,
const char* move,
int (*movecallback)(const char* move, void* userdata), void* userdata);
// Pass the user move to the engine to which the engine will respond
// with its move.
// The move must be done as Coordinate Algebraic Notation (a2a3 etc)
// unless the engine info on startup contained "SAN" : "1",
// in which case it MUST be specified as Standard Algebraic Notation
// as used in PGN (a5, Bc6+, O-O-O etc).
// The callback works similarly as for chessinterface_Go.

// Update the clock time left:
void chessinterface_UpdateClockTime(
const struct chessinterfaceengine* engine,
int engineSeconds, int userSeconds);
// You should call this after the engine transmitted a move,
// and instantly before you use chessinterface_Usermove or
// chessinterface_Go to keep the engine up to date on the
// thinking time.
// Please note at the start of the game, you should have called
// chessinterface_SetTimeControl first before calling this.

// Tell engine to move NOW (only does something if engine
// is calculating a move):
void chessinterface_MoveNow(struct chessinterfaceengine* engine);
// Please note this only asks the engine to move as soon as possible,
// however it doesn't force it to do so. Some engines might still
// take a second or longer to react, and others might ignore your
// request entirely.

// Offer the engine a draw:
void chessinterface_Userdraw(struct chessinterfaceengine* engine);
// If the engine accepts the draw, it will call the draw
// callback supplied with chessinterface_StartGame.
// In that case, you may use chessinterface_Result to end
// the game officially with a draw.
// If the engine doesn't trigger the callback, the game
// must continue regularly.

// Pause the game (only possible if engine is NOT calculating a move
// right now, if it does please wait until you received it):
void chessinterface_Pause(struct chessinterfaceengine* engine);
// This simply tells the engine to pause its clocks.
// As soon as you use chessinterface_Go() or chessinterface_Usermove()
// the next time, the game will continue.

// Set position to given FEN string.
int chessinterface_SetFEN(struct chessinterfaceengine* engine,
const char* fen);
// Depending on the chess variant you play, you may need to
// consult
// http://http://www.open-aurec.com/wbforum/WinBoard/engine-intf.html
// for the variant-specific alterations to FEN.
// If a game is currently running, it will be paused (similar to
// chessinterface_Pause) use chessinterface_Go/chessinterface_Usermove
// to resume.

// If you want, you can pass the engine the result
// at the end of a match:
void chessinterface_Result(struct chessinterfaceengine* engine,
const char* result);
// For result, you can pass 0-1, 1-0 or 1-2/1-2.
// You should do this instantly after either getting the
// engine move that ends the game or after sending the user move
// with chessinterface_Usermove() that ends the game.

// Close a chess engine:
void chessinterface_Close(struct chessinterfaceengine* engine);

#endif  // CHESSINTERFACE_H_

