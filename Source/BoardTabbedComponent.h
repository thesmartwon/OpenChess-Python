/*
  ==============================================================================

  This is an automatically generated GUI class created by the Introjucer!

  Be careful when adding custom code to these files, as only the code within
  the "//[xyz]" and "//[/xyz]" sections will be retained when the file is loaded
  and re-saved.

  Created with Introjucer version: 3.1.0

  ------------------------------------------------------------------------------

  The Introjucer is part of the JUCE library - "Jules' Utility Class Extensions"
  Copyright 2004-13 by Raw Material Software Ltd.

  ==============================================================================
*/

#ifndef __JUCE_HEADER_14880CE2C5F867EA__
#define __JUCE_HEADER_14880CE2C5F867EA__

//[Headers]     -- You can add your own extra header files here --
#include "BoardComponent.h"
#include "JuceHeader.h"

//[/Headers]



//==============================================================================
/**
                                                                    //[Comments]
    An auto-generated component, created by the Introjucer.

    Describe your class and how it works here!
                                                                    //[/Comments]
*/
class BoardTabbedComponent  : public Component,
                              public MessageListener
{
public:
    //==============================================================================
    BoardTabbedComponent (juce::Array<Image> boardImages);
    ~BoardTabbedComponent();

    //==============================================================================
    //[UserMethods]     -- You can add your own custom methods in this section.
    //[/UserMethods]

    void paint (Graphics& g);
    void resized();



private:
    //[UserVariables]   -- You can add your own custom variables in this section.
    Stockfish::Position position;
    void handleMessage (const Message & message) override;
    //[/UserVariables]

    //==============================================================================
    ScopedPointer<TextEditor> txtMoveHist;
    ScopedPointer<BoardComponent> cmpBoard;
    ScopedPointer<TextEditor> txtEngineOutput;


    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (BoardTabbedComponent)
};

//[EndFile] You can add extra defines here...
//[/EndFile]

#endif   // __JUCE_HEADER_14880CE2C5F867EA__
