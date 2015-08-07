#include "MainWindow.h"

static ScopedPointer<ApplicationCommandManager> applicationCommandManager;
static ScopedPointer<AudioDeviceManager> sharedAudioDeviceManager;

MainWindow::MainWindow (String name)
    : DocumentWindow(name,
                   Colours::lightgrey,
                   DocumentWindow::allButtons) 
{
    setUsingNativeTitleBar (true);
    //mainContentComponent = new MainContentComponent ();
    setContentOwned (new MainComponent (), true);

    centreWithSize (getWidth (), getHeight ());
    setVisible (true);
    setResizable (true, false);

    // this lets the command manager use keypresses that arrive in our window to send out commands
    addKeyListener (getApplicationCommandManager ().getKeyMappings ());

    triggerAsyncUpdate ();


    #if JUCE_OPENGL
        openGLContext.attachTo (*getTopLevelComponent ());
    #endif
}

MainWindow::~MainWindow ()
{
    applicationCommandManager = nullptr;
    sharedAudioDeviceManager = nullptr;

    #if JUCE_OPENGL
        openGLContext.detach ();
    #endif
}

void MainWindow::closeButtonPressed ()
{
    // This is called when the user tries to close this window. Here, we'll just
    // ask the app to quit when this happens, but you can change this to do
    // whatever you need.
    JUCEApplication::getInstance ()->systemRequestedQuit ();
}

// (return the command manager object used to dispatch command events)
ApplicationCommandManager& MainWindow::getApplicationCommandManager ()
{
    if (applicationCommandManager == nullptr)
        applicationCommandManager = new ApplicationCommandManager ();

    return *applicationCommandManager;
}

// (returns a shared AudioDeviceManager object that all the demos can use)
AudioDeviceManager& MainWindow::getSharedAudioDeviceManager ()
{
    if (sharedAudioDeviceManager == nullptr)
    {
        sharedAudioDeviceManager = new AudioDeviceManager ();
        sharedAudioDeviceManager->initialise (2, 2, 0, true, String::empty, 0);
    }

    return *sharedAudioDeviceManager;
}

void MainWindow::handleAsyncUpdate ()
{
    // This registers all of our commands with the command manager but has to be done after the window has
    // been created so we can find the number of rendering engines available
    ApplicationCommandManager& commandManager = MainWindow::getApplicationCommandManager ();
    commandManager.registerAllCommandsForTarget (JUCEApplication::getInstance ());
}