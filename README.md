# Open Chess
This is an cross-platform open-source Chess GUI written in python3.5 that can be used for playing or analyzing large amounts of chess games.
## Building
1. Use Python 3.5.x (I'm using [3.5.1](https://www.python.org/downloads/release/python-35/))
2. Install the [SIP 4.18 whl](https://www.riverbankcomputing.com/software/sip/download) with `pip install sip-4.18...`.
3. Install the [PyQt5.6 whl](https://www.riverbankcomputing.com/software/pyqt/download5) with `pip install PyQt5.6...`.
4. Install python-chess with `pip install python-chess`.
5. Run `python src/main.py` and that's it!

## Philosophy
The goal is to keep the board and the game of chess, not the features, the focus. I want chess to be simple, fun, and videogame-like. All the (useful, widely-used) features in ChessBase are to be supported.

There are some problems that I have with current chess GUIs:
- There's too much going on at every screen.
    - Less clutter will attract new chess players and encourage them to play chess more.
- There isn't an all-in-one beginner to master lesson plan for free anywhere on the internet. Let alone one that is interactive.
    - Chess boils down to quick pattern recognition. Training lessons should be like playing a video-game: fun and simple.
    - See lessons.txt
- Cannot analyze multiple games at once (or is very finicky).
- Lack of mobile support.
    - There are no good apps on Android/iOS that will train someone from beginner to FM level given that they have enough dedication. After release 1.0, all my attention will be turned to an Android/iOS release.

## Roadmap
I want to make Open Chess the perfect companion for lichess.org, and chess training in general. Below is what I'm going to do next.

### Base
- General
	- Logging streams
1. (done) Board follows rules
	- Board editing
	- Board premoving
	- Board moves undo/redoable
2. (done) Movetree
3. (done) Engine analysis pane
	- Add engine variation to game
	- Computer gauge
	- Make tableview instead of long text
4. (in progress) Full variation support
	- Editing game headers
	- Game annotating (some graphical buttons and icons for game annotators to make and view annotated pgns)
	- Opening type as header
	- White/black resign buttons
	- +/- pawns in moveTree
	- Default overwrite/add setting
5. Game commentating (drawing arrows, circles, and squares various for youtube videos/lessons)
6. Advantage over time graph
7. Endgame explorer (and some theory training)
8. Opening explorer (and some theory training)

### After Base
1. Code purging/bug handling/making unit tests

### Essential
1. Lesson plans for Beginner/Intermediate/Expert
	- Tactics puzzles (lots of mate in X)
	- Endgame puzzles
	- Opening puzzles
2. Practice against the engine between lessons. Have the machine try out many different decent moves
3. Game analysis like lichess', except live

### Icing
1. A page about how Stockfish works
2. Convenient game library with searching
3. Statistics and stat tracking on nearly EVERYTHING. Personal profile page. Lots of graphs.
4. Screenshot to FEN
5. Printing games


Check back often to see the progress!

## Deploying
Eventually, I will be using SIP and pyqtdeploy. It will be a pain, but worth it.
