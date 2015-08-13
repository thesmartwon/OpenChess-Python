#include "MainWindow.h"

static ScopedPointer<ApplicationCommandManager> applicationCommandManager;

MainWindow::MainWindow (String name)
    : DocumentWindow(name,
                   Colours::lightgrey,
                   DocumentWindow::allButtons) 
{
    setUsingNativeTitleBar (true);
    //mainContentComponent = new MainContentComponent ();
    setContentOwned (mainComponent = new MainContentComponent (), true);

    centreWithSize (getWidth (), getHeight ());
    setVisible (true);
    setResizable (true, true);

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

void MainWindow::handleAsyncUpdate ()
{
    // This registers all of our commands with the command manager but has to be done after the window has
    // been created so we can find the number of rendering engines available
    ApplicationCommandManager& commandManager = MainWindow::getApplicationCommandManager ();
    commandManager.registerAllCommandsForTarget (JUCEApplication::getInstance ());
}

MainWindow* MainWindow::getMainWindow ()
{
    for (int i = TopLevelWindow::getNumTopLevelWindows (); --i >= 0;)
        if (MainWindow* maw = dynamic_cast<MainWindow*> (TopLevelWindow::getTopLevelWindow (i)))
        return maw;

    return nullptr;
}

void MainWindow::showMessageBubble (const String& text)
{
    currentBubbleMessage = new BubbleMessageComponent (500);
    getContentComponent ()->addChildComponent (currentBubbleMessage);

    AttributedString attString;
    attString.append (text, Font (15.0f));

    currentBubbleMessage->showAt (juce::Rectangle<int> (getLocalBounds ().getCentreX (), 10, 1, 1),
        attString,
        500,  // numMillisecondsBeforeRemoving
        true,  // removeWhenMouseClicked
        false); // deleteSelfAfterUse
}