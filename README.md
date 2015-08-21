# Open Chess
This is an cross-platform open-source Chess GUI written in C++ that can be used for playing or analyzing large amounts of chess games.

It is still in development, but the plan is that it would someday be a free alternative to programs like ChessBase.

Check the TODO.txt for a list of features I'm planning on adding!

## Building
OpenChess should build out of the box just fine on any master commit -- look in the Builds folder and fire up your IDE of choice. You'll have to copy over the Resources folder to wherever the applications current working directory is. The JUCE dependencies have all been copied over (they aren't very big).

VS2015 might be tricky though because I use precompiled headers and keep it updated separately from the other auto-generated Introjucer builds. If it doesn't work, just use another build.

That being said, if you want the best development experience (or it doesn't build for some reason), then Open Chess' only dependency is JUCE, a cross-platform C++ GUI library available [here.](http://www.juce.com/download) Simply install JUCE, and then open the OpenChess.jucer with the Introjucer. It'll take care of your platform specific needs, and has a handy GUI tool that I use (it edits code though, so be careful!).