#ifndef MAINWINDOW_H_INCLUDED
#define MAINWINDOW_H_INCLUDED

#include "JuceHeader.h"
#include "MainContentComponent.h"

class MainWindow     : public DocumentWindow,
                       private AsyncUpdater
{
public:
    MainWindow (String name);

    ~MainWindow ();

    static MainWindow* getMainWindow (); // returns the MainWindow if it exists.
                                               
    void closeButtonPressed () override;// called by the OS when the window's close button is pressed.

    // (return the command manager object used to dispatch command events)
    static ApplicationCommandManager& getApplicationCommandManager ();

    /* Note: Be careful if you override any DocumentWindow methods - the base
    class uses a lot of them, so by overriding you might break its functionality.
    It's best to do all your work in your content component instead, but if
    you really have to override any DocumentWindow methods, make sure your
    subclass also calls the superclass's method.
    */

private:
    //ScopedPointer<Component> mainContentComponent;
    ScopedPointer<Component> mainComponent;
    ScopedPointer<BubbleMessageComponent> currentBubbleMessage;
    void handleAsyncUpdate () override;

    TooltipWindow tooltipWindow; // to add tooltips to an application, you
                                 // just need to create one of these and leave it
                                 // there to do its work..

    //#if JUCE_OPENGL
    //    OpenGLContext openGLContext;
    //#endif


    void showMessageBubble (const String&);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainWindow)
};

#endif //MAINWINDOW_H_INCLUDED