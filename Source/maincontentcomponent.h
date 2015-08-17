/*
  ==============================================================================

    This file was auto-generated!

  ==============================================================================
*/

#ifndef MAINCOMPONENT_H_INCLUDED
#define MAINCOMPONENT_H_INCLUDED

#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardTabbedComponent.h"
#include "MainWindow.h"

//==============================================================================
/*
    This component lives inside our window, and this is where you should put all
    your controls and content.
*/
class MainContentComponent   : public Component,
							   public MenuBarModel,
							   public ApplicationCommandTarget
{
public:
    //==============================================================================
    MainContentComponent ();
    ~MainContentComponent ();
    
    StringArray getMenuBarNames () override;
    PopupMenu getMenuForIndex (int menuIndex, const String &) override;
    void menuItemSelected (int menuItemID, int) override;
    void paint (Graphics&);
    void resized();

private:
    //==============================================================================
    ScopedPointer<BoardTabbedComponent> boardTabbedComponent;
    ScopedPointer<MenuBarComponent> menuBar;
    ApplicationCommandTarget * getNextCommandTarget () override;
    bool perform (const InvocationInfo & info) override;
    void getAllCommands (Array<CommandID>& commands) override;
    void getCommandInfo (CommandID commandID, ApplicationCommandInfo & result) override;
    PopupMenu getDummyPopupMenu ();
    int menuBarHeight;

    LookAndFeel_V1 lookAndFeelV1;
    LookAndFeel_V2 lookAndFeelV2;
    LookAndFeel_V3 lookAndFeelV3;

    OpenGLContext openGLContext;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainContentComponent)
};


#endif  // MAINCOMPONENT_H_INCLUDED

