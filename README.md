# Open Chess
This is an cross-platform open-source Chess GUI written in python that can be used for playing or analyzing large amounts of chess games.

It is still in its very early stages of development, but the plan is that it would someday be a free alternative to programs like ChessBase.
There are some problems that I have with current chess GUIs:
- There's too much going on at every screen. Every program has too many buttons and is like flying a space shuttle.
    - I'd rather have simple and intuitive menus to find a feature IF and when I want it.
    - Each button needs to be labeled correctly and intuitively placed.
    - Less clutter will attract new chess players and encourage them to play chess more.
    - I want the board and the game of chess, not the features, to be the focus.
    - I want GUIs to be very fluid and responsive.
- There isn't an all-in-one beginner to master lesson plan for free anywhere on the internet. Let alone one that is interactive
    - I want to create a suite of lessons where you train quickly against StockFish. Chess boils down to quick pattern recognition.
- Each GUI is missing some quintessential features.
    - Simple things like viewing the advantage over time graph that is ugly (and broken) in Arena, or 'how many times is each square attacked and defended?'.
    - Each essential feature needs to be up front and visible.
        - Advantage over time graph, opening explorer, endgame explorer, movetree, lesson/puzzle guide, library page, statistics page, and engine output.
    - They don't ship with opening books/endgame tablebases and it's a pain to find and use the proper ones.
        - I want to just use lichess' two databases.
        - I also want to just use Syzygy tablebases with a download link below them.
    - Tactics/bestmove training positions and recordkeeping
- Cannot anaylze multiple games at once (or is very finicky).
- Lack of mobile support.
    - Basically only DroidFish exists right now. After PC release, all my attention will be turned to Android/Apple release.
    - I want to sync up user games between the two and implement the most popular features.

I want to make Open Chess the perfect companion for lichess.org/chess.com.
Besides various 'TODO's in the code, I am planning on eventually adding:
- 1,000,000 customizations for the board (I believe look and feel of the board is the most important part of a GUI)
- Advantage over time graph
- Endgame explorer (and some theory training)
- Opening explorer (and some theory training)
- Tactics puzzles (lots of mate in X)
- Lesson plans for Beginner/Intermediate/Expert (I have this all planned out in a separate doc)
- Statistics and stat tracking on nearly EVERYTHING. Personal profile page. Lots of graphs.
- A page with descriptions about how stockfish works
- Convenient game library with searching
- Game analysis like lichess', except live
- Practice against the engine between lessons. Have the machine try out many different decent moves.
- Game commentating (drawing arrows, circles, and squares various for youtube videos/lessons)
- Game annotating (some graphical buttons and icons for game annotators to make and view annotated pgns)


Check back for more features in the future!


## Building
Install PyQt5 and run `pip install python-chess` on python 3.4. Then run main.py and that's it!