# Open Chess
## Building
1. Use Python 3.4.x (I'm using [3.4.4](https://www.python.org/downloads/release/python-344/))
2. Install [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
3. Run `pip install python-chess` (make sure on python 3.4.x)
4. Run `python3 main.py` and that's it!
This is an cross-platform open-source Chess GUI written in python that can be used for playing or analyzing large amounts of chess games.

## Philosophy
It is still in its very early stages of development, but the plan is that it would someday be a free alternative to programs like ChessBase.
Keep it simple, fun, and videogame-like. Keep the board and the game of chess, not the features, the focus.

There are some problems that I have with current chess GUIs:
- There's too much going on at every screen.
    - Less clutter will attract new chess players and encourage them to play chess more.
- There isn't an all-in-one beginner to master lesson plan for free anywhere on the internet. Let alone one that is interactive.
    - Chess boils down to quick pattern recognition. Training lessons should be like playing a video-game: fun and simple.
    - See lessons.txt
- Cannot anaylze multiple games at once (or is very finicky).
- Lack of mobile support.
    - There are no good apps on Android/iOS that will train from beginner to NM level. After release 1.0, all my attention will be turned to an Android/iOS release.

## Roadmap
I want to make Open Chess the perfect companion for lichess.org, and chess training in general.
Base
- (done) Pieces follow rules
- (done) Movetree
- (done) Engine analysis pane
- Game commentating (drawing arrows, circles, and squares various for youtube videos/lessons)
- Game annotating (some graphical buttons and icons for game annotators to make and view annotated pgns)
- Advantage over time graph
- Endgame explorer (and some theory training)
- Opening explorer (and some theory training)
Essential
- Lesson plans for Beginner/Intermediate/Expert
	- Tactics puzzles (lots of mate in X)
	- Endgame puzzles
	- Opening puzzles
- Practice against the engine between lessons. Have the machine try out many different decent moves
- Game analysis like lichess', except live

Icing
- A page about how Stockfish works
- Convenient game library with searching
- Statistics and stat tracking on nearly EVERYTHING. Personal profile page. Lots of graphs.


Check back often to see the progress!

## Deploying
Eventually, I will be using pyqtdeploy and SIP. It will be a pain, but worth it.
