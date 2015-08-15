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

//[/Headers]

#include "BoardTabsComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabsComponent::BoardTabsComponent ()
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
    //[/Constructor_pre]

    addAndMakeVisible (boardsComponent = new TabbedComponent (TabbedButtonBar::TabsAtTop));
    boardsComponent->setTabBarDepth (30);
    boardsComponent->addTab (TRANS("Game 0"), Colours::lightgrey, new BoardTabbedComponent (boardImages), true);
    boardsComponent->addTab (TRANS("Game 1"), Colours::lightgrey, new BoardTabbedComponent (boardImages), true);
    boardsComponent->setCurrentTabIndex (0);


    //[UserPreSize]
    //[/UserPreSize]

    setSize (1351, 778);


    //[Constructor] You can add your own custom stuff here..
    setOpaque (true);
    //setSize (getBoundsInParent ().getWidth (), getBoundsInParent ().getHeight ());
    //[/Constructor]
}

BoardTabsComponent::~BoardTabsComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]

    boardsComponent = nullptr;


    //[Destructor]. You can add your own custom destruction code here..
    //[/Destructor]
}

//==============================================================================
void BoardTabsComponent::paint (Graphics& g)
{
    //[UserPrePaint] Add your own custom painting code here..
    //[/UserPrePaint]

    g.fillAll (Colours::white);

    //[UserPaint] Add your own custom painting code here..
    //[/UserPaint]
}

void BoardTabsComponent::resized()
{
    //[UserPreResize] Add your own custom resize code here..
    //[/UserPreResize]

    boardsComponent->setBounds (0, 0, proportionOfWidth (1.0000f), proportionOfHeight (1.0000f));
    //[UserResized] Add your own custom resize handling here..
    //[/UserResized]
}



//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...
//[/MiscUserCode]


//==============================================================================
#if 0
/*  -- Introjucer information section --

    This is where the Introjucer stores the metadata that describe this GUI layout, so
    make changes in here at your peril!

BEGIN_JUCER_METADATA

<JUCER_COMPONENT documentType="Component" className="BoardTabsComponent" componentName=""
                 parentClasses="public Component" constructorParams="" variableInitialisers=""
                 snapPixels="8" snapActive="1" snapShown="1" overlayOpacity="0.330"
                 fixedSize="0" initialWidth="1351" initialHeight="778">
  <BACKGROUND backgroundColour="ffffffff"/>
  <TABBEDCOMPONENT name="boards component" id="55247761818d8fa8" memberName="boardsComponent"
                   virtualName="" explicitFocusOrder="0" pos="0 0 100% 100%" orientation="top"
                   tabBarDepth="30" initialTab="0">
    <TAB name="Game 0" colour="ffd3d3d3" useJucerComp="0" contentClassName="BoardTabbedComponent"
         constructorParams="boardImages" jucerComponentFile=""/>
    <TAB name="Game 1" colour="ffd3d3d3" useJucerComp="0" contentClassName="BoardTabbedComponent"
         constructorParams="boardImages" jucerComponentFile=""/>
  </TABBEDCOMPONENT>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
