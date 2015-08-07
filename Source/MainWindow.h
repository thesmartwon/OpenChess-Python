#ifndef MAINWINDOW_H_INCLUDED
#define MAINWINDOW_H_INCLUDED

#include "JuceHeader.h"
#include "MainComponent.h"

class MainWindow     : public DocumentWindow,
                       private AsyncUpdater
{
public:
    MainWindow (String name);

    ~MainWindow ();

    void closeButtonPressed () override;

    // (return the command manager object used to dispatch command events)
    static ApplicationCommandManager& getApplicationCommandManager ();

    // (returns a shared AudioDeviceManager object that all the demos can use)
    AudioDeviceManager& getSharedAudioDeviceManager ();

    /* Note: Be careful if you override any DocumentWindow methods - the base
    class uses a lot of them, so by overriding you might break its functionality.
    It's best to do all your work in your content component instead, but if
    you really have to override any DocumentWindow methods, make sure your
    subclass also calls the superclass's method.
    */

private:
    //ScopedPointer<Component> mainContentComponent;
    //ScopedPointer<MainContentComponent> mainContentComponent;
    void handleAsyncUpdate () override;

    #if JUCE_OPENGL
        OpenGLContext openGLContext;
    #endif

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainWindow)
};

#endif //MAINWINDOW_H_INCLUDED