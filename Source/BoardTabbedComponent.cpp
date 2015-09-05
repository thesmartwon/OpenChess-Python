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

//[Headers] You can add your own extra header files here...
#include "stdafx.h"
//[/Headers]

#include "BoardTabbedComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabbedComponent::BoardTabbedComponent ()
{
    //[Constructor_pre] You can add your own custom stuff here..
    boardImages.add (ImageCache::getFromFile (File::getCurrentWorkingDirectory ().getChildFile ("/Resources/board.jpg")));
    boardImages.add (ImageCache::getFromFile (File::getCurrentWorkingDirectory ().getChildFile ("/Resources/Chess_Pieces_Sprite.png")));

    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (0, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 2, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 3, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 4, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 5, 0, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));

    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (0, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 2, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 3, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 4, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.add (boardImages[1].getClippedImage (juce::Rectangle<int> (boardImages[1].getWidth () / 6.0 * 5, boardImages[1].getHeight () / 2, boardImages[1].getWidth () / 6.0, boardImages[1].getHeight () / 2)));
    boardImages.remove (1); //don't need the image with all the pieces anymore
    int boardWidth = 720;
    int squareWidth = boardWidth / 8;
    boardImages.add (boardImages[0].rescaled (boardWidth, boardWidth));
    boardImages.add (boardImages[1].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[2].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[3].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[4].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[5].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[6].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[7].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[8].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[9].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[10].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[11].rescaled (squareWidth, squareWidth));
    boardImages.add (boardImages[12].rescaled (squareWidth, squareWidth));
    //[/Constructor_pre]

    addAndMakeVisible (tabbedComponent = new TabbedComponent (TabbedButtonBar::TabsAtTop));
    tabbedComponent->setTabBarDepth (30);
    tabbedComponent->setCurrentTabIndex (-1);

    addAndMakeVisible (newTabButton = new TextButton ("new button"));
    newTabButton->setTooltip (TRANS("New Tab"));
    newTabButton->setButtonText (TRANS("+"));
    newTabButton->addListener (this);
    newTabButton->setColour (TextButton::buttonColourId, Colours::white);


    //[UserPreSize]
    tabComponents.add (new BoardTabComponent (boardImages));
    tabbedComponent->addTab (TRANS("Game 0"), Colours::lightgrey, tabComponents[0], false);
    tabbedComponent->setCurrentTabIndex (0);
    //newTabButton->setBounds(tabbedComponent->getTabbedButtonBar().get)
    //[/UserPreSize]

    setSize (1351, 778);


    //[Constructor] You can add your own custom stuff here..
    setOpaque (true);
    //setSize (getBoundsInParent ().getWidth (), getBoundsInParent ().getHeight ());
    //[/Constructor]
}

BoardTabbedComponent::~BoardTabbedComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]

    tabbedComponent = nullptr;
    newTabButton = nullptr;


    //[Destructor]. You can add your own custom destruction code here..
    //[/Destructor]
}

//==============================================================================
void BoardTabbedComponent::paint (Graphics& g)
{
    //[UserPrePaint] Add your own custom painting code here..
    //[/UserPrePaint]

    g.fillAll (Colours::white);

    //[UserPaint] Add your own custom painting code here..
    //[/UserPaint]
}

void BoardTabbedComponent::resized()
{
    //[UserPreResize] Add your own custom resize code here..
    //[/UserPreResize]

    tabbedComponent->setBounds (0, 0, proportionOfWidth (1.0000f), proportionOfHeight (1.0000f));
    newTabButton->setBounds (144, 0, 30, 30);
    //[UserResized] Add your own custom resize handling here..
    //[/UserResized]
}

void BoardTabbedComponent::buttonClicked (Button* buttonThatWasClicked)
{
    //[UserbuttonClicked_Pre]
    //[/UserbuttonClicked_Pre]

    if (buttonThatWasClicked == newTabButton)
    {
        //[UserButtonCode_newTabButton] -- add your button handler code here..
        //[/UserButtonCode_newTabButton]
    }

    //[UserbuttonClicked_Post]
    //[/UserbuttonClicked_Post]
}



//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...
void BoardTabbedComponent::undoMove ()
{
    tabComponents[tabbedComponent->getCurrentTabIndex ()]->undoMove();
}

void BoardTabbedComponent::redoMove ()
{
    tabComponents[tabbedComponent->getCurrentTabIndex ()]->redoMove ();
}
//[/MiscUserCode]


//==============================================================================
#if 0
/*  -- Introjucer information section --

    This is where the Introjucer stores the metadata that describe this GUI layout, so
    make changes in here at your peril!

BEGIN_JUCER_METADATA

<JUCER_COMPONENT documentType="Component" className="BoardTabbedComponent" componentName=""
                 parentClasses="public Component" constructorParams="" variableInitialisers=""
                 snapPixels="8" snapActive="1" snapShown="1" overlayOpacity="0.330"
                 fixedSize="0" initialWidth="1351" initialHeight="778">
  <BACKGROUND backgroundColour="ffffffff"/>
  <TABBEDCOMPONENT name="new tabbed component" id="d965c7f735419935" memberName="tabbedComponent"
                   virtualName="" explicitFocusOrder="0" pos="0 0 100% 100%" orientation="top"
                   tabBarDepth="30" initialTab="-1"/>
  <TEXTBUTTON name="new button" id="5ebb34b59ff32d81" memberName="newTabButton"
              virtualName="" explicitFocusOrder="0" pos="144 0 30 30" tooltip="New Tab"
              bgColOff="ffffffff" buttonText="+" connectedEdges="0" needsCallback="1"
              radioGroupId="0"/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
