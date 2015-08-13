/*
  ==============================================================================

    This file was auto-generated!

  ==============================================================================
*/

#ifndef MAINCOMPONENT_H_INCLUDED
#define MAINCOMPONENT_H_INCLUDED

#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardTabsComponent.h"
#include "MainWindow.h"

//==============================================================================
/*
    This component lives inside our window, and this is where you should put all
    your controls and content.
*/
class ContentComponent   : public Component,
                           public MenuBarModel,
                           public ApplicationCommandTarget
{
public:
    ApplicationCommandTarget * getNextCommandTarget () override;
    bool perform (const InvocationInfo & info) override;
    void getAllCommands (Array<CommandID>& commands) override {};
    void getCommandInfo (CommandID commandID, ApplicationCommandInfo & result) override {};
    //==============================================================================
    ContentComponent ();
    ~ContentComponent ();
    
    StringArray getMenuBarNames () override;
    PopupMenu getMenuForIndex (int menuIndex, const String &) override;
    void menuItemSelected (int menuItemID, int) override;
    void paint (Graphics&);
    void resized();

private:
    //==============================================================================
    ScopedPointer<BoardTabsComponent> boardTabsComponent;
    ScopedPointer<MenuBarComponent> menuBar;
    PopupMenu getDummyPopupMenu ();
    


    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ContentComponent)
};


#endif  // MAINCOMPONENT_H_INCLUDED

