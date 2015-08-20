/*
  ==============================================================================

  This is an automatically generated GUI class created by the Introjucer!

  Be careful when adding custom code to these files, as only the code within
  the "//[xyz]" and "//[/xyz]" sections will be retained when the file is loaded
  and re-saved.

  Created with Introjucer version: 3.2.0

  ------------------------------------------------------------------------------

  The Introjucer is part of the JUCE library - "Jules' Utility Class Extensions"
  Copyright (c) 2015 - ROLI Ltd.

  ==============================================================================
*/

#ifndef __JUCE_HEADER_B83DEE5E40890FBC__
#define __JUCE_HEADER_B83DEE5E40890FBC__

//[Headers]     -- You can add your own extra header files here --
#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardComponent.h"
#include "MoveListComponent.h"
#include "BoardPosition/game.h"
#include "types.h"
#include <sstream>
#include <iomanip>

//[/Headers]



//==============================================================================
/**
                                                                    //[Comments]
    An auto-generated component, created by the Introjucer.

    Describe your class and how it works here!
                                                                    //[/Comments]
*/
class BoardTabComponent  : public Component,
                           public MessageListener
{
public:
    //==============================================================================
    BoardTabComponent (juce::Array<Image> boardImages);
    ~BoardTabComponent();

    //==============================================================================
    //[UserMethods]     -- You can add your own custom methods in this section.
    void undoMove();
    void redoMove();
    //[/UserMethods]

    void paint (Graphics& g);
    void resized();



private:
    //[UserVariables]   -- You can add your own custom variables in this section.
    Game activeGame;
    void handleMessage (const Message & message) override;
    MoveListComponent* moveListComp;
    void updatePosition ();
    //[/UserVariables]

    //==============================================================================
    ScopedPointer<BoardComponent> boardComponent;
    ScopedPointer<TextEditor> engineOutputText;
    ScopedPointer<Viewport> moveListView;


    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (BoardTabComponent)
};

//[EndFile] You can add extra defines here...
//[/EndFile]

#endif   // __JUCE_HEADER_B83DEE5E40890FBC__
