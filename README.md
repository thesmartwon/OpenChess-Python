# Open Chess
This is an cross-platform open-source Chess GUI written in C++ that can be used for playing or analyzing large amounts of chess games.
It is still in development, but the plan is that it would someday be a free alternative to programs like ChessBase.
Check the TODO.txt for a list of features I'm planning on adding!

## Building
OpenChess should build out of the box just fine on any master commit -- just look in the Builds folder and fire up your IDE of choice. You'll have to copy over the Resources folder to wherever the applications current working directory is though. The dependencies have all been copied over (they aren't very big).
That being said, if you want the best development experiance (or it doesn't build for some reason), Open Chess' only dependency is JUCE, a cross-platform C++ GUI library available [here.](http://www.juce.com/download) Simply install JUCE, run the Introjucer that comes with it, and open the OpenChess.jucer inside that program. It'll take care of your platform specific needs, and has a handy GUI tool that I use (it edits the code though, be careful). I'm very excited for the next version of JUCE to come out that will make my even lot easier than it already is!