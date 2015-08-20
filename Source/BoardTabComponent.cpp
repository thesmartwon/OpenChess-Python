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

#include "BoardTabComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabComponent::BoardTabComponent (juce::Array<Image> boardImages)
{
    //[Constructor_pre] You can add your own custom stuff here..
    //[/Constructor_pre]

    addAndMakeVisible (boardComponent = new BoardComponent (boardImages, &activeGame));
    boardComponent->setName ("new board");

    addAndMakeVisible (engineOutputText = new TextEditor ("new text editor"));
    engineOutputText->setMultiLine (true);
    engineOutputText->setReturnKeyStartsNewLine (false);
    engineOutputText->setReadOnly (true);
    engineOutputText->setScrollbarsShown (true);
    engineOutputText->setCaretVisible (false);
    engineOutputText->setPopupMenuEnabled (false);
    engineOutputText->setText (TRANS("Engine output"));

    addAndMakeVisible (moveListView = new Viewport ("new viewport"));
    moveListView->setScrollBarsShown (false, false);


    //[UserPreSize]
    moveListView->setViewedComponent (moveListComp = new MoveListComponent());
    //[/UserPreSize]

    setSize (1351, 748);


    //[Constructor] You can add your own custom stuff here..
    //setSize (getBoundsInParent ().getWidth (), getBoundsInParent ().getHeight ());

    //[/Constructor]
}

BoardTabComponent::~BoardTabComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]

    boardComponent = nullptr;
    engineOutputText = nullptr;
    moveListView = nullptr;


    //[Destructor]. You can add your own custom destruction code here..
    //[/Destructor]
}

//==============================================================================
void BoardTabComponent::paint (Graphics& g)
{
    //[UserPrePaint] Add your own custom painting code here..
    //[/UserPrePaint]

    g.fillAll (Colours::white);

    //[UserPaint] Add your own custom painting code here..
    //[/UserPaint]
}

void BoardTabComponent::resized()
{
    //[UserPreResize] Add your own custom resize code here..
    //[/UserPreResize]

    boardComponent->setBounds (5, 5, proportionOfWidth (0.5389f), proportionOfHeight (0.9826f));
    engineOutputText->setBounds (getWidth() - 8 - proportionOfWidth (0.4478f), getHeight() - 8 - proportionOfHeight (0.2166f), proportionOfWidth (0.4478f), proportionOfHeight (0.2166f));
    moveListView->setBounds (getWidth() - 7 - proportionOfWidth (0.4478f), 5, proportionOfWidth (0.4478f), proportionOfHeight (0.7540f));
    //[UserResized] Add your own custom resize handling here..
    const int moveListViewWidth = moveListView->getVerticalScrollBar ()->isVisible () ?
                                  moveListView->getWidth() - moveListView->getVerticalScrollBar ()->getWidth () :
                                  moveListView->getWidth ();
    juce::Rectangle<int> moveListViewBounds = moveListView->getBounds ();
    moveListViewBounds.setWidth (moveListViewWidth);
    moveListView->getViewedComponent()->setBounds (moveListViewBounds);
    if (getHeight () - boardComponent->getHeight () + 8 > engineOutputText->getHeight ())
    { //engine output can fit under board
        engineOutputText->setBounds (boardComponent->getX (),
                                     boardComponent->getHeight () + 8,
                                     boardComponent->getWidth (),
                                     getHeight() - boardComponent->getHeight () - 8 - 5);
        moveListViewBounds = moveListView->getBounds ();
        moveListViewBounds.setHeight (proportionOfHeight (0.9845f));
        moveListView->setBounds (moveListViewBounds);
        moveListView->getViewedComponent ()->setBounds (getWidth () - 7 - proportionOfWidth (0.4449f),
            5,
            moveListViewWidth,
            proportionOfHeight (0.9845f));
    }
    //[/UserResized]
}



//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...
void BoardTabComponent::updatePosition()
{
    moveListComp->updateMoveList (&activeGame);
}

void BoardTabComponent::undoMove()
{
	activeGame.undoMove();
    updatePosition();
}

void BoardTabComponent::redoMove ()
{
	activeGame.redoMove();
    updatePosition();
}

void BoardTabComponent::handleMessage (const Message & message)
{
    // this method is called by the board when a (half) move has happened, so we should send the info
    // other places.

    if (((GenericMessage*)(&message))->messageType == MSG_MOVEMESSAGE)
    {
        //update movelist
        MoveMessage* moveMessage = ((MoveMessage*)(&message));
		juce::String moveText = moveMessage->moveSAN;

        MoveNode* newNode = new MoveNode();
        newNode->parent = activeGame.getCurrentlyViewedNode ();
        newNode->comments = String::empty;
        newNode->continuation = nullptr;
        newNode->move = moveMessage->move;
        newNode->variation = nullptr;
        String labelText;
        if (activeGame.getCurrentlyViewedPosition().game_ply () % 2 == 1)
            labelText = std::to_string (activeGame.getCurrentlyViewedPosition ().game_ply () - activeGame.getCurrentlyViewedPosition ().game_ply () / 2) + ". " + moveText, NotificationType::dontSendNotification;
        else
            labelText = moveText + " ";
		newNode->moveLabelText = labelText;
		Stockfish::Position newPos(activeGame.getCurrentlyViewedPosition());
		newPos.do_move(newNode->move, *(Stockfish::StateInfo *)calloc(1, sizeof(Stockfish::StateInfo)));
		newNode->position = newPos;
        activeGame.appendMoveToMainline (newNode);
        updatePosition ();
    }
}
//[/MiscUserCode]


//==============================================================================
#if 0
/*  -- Introjucer information section --

    This is where the Introjucer stores the metadata that describe this GUI layout, so
    make changes in here at your peril!

BEGIN_JUCER_METADATA

<JUCER_COMPONENT documentType="Component" className="BoardTabComponent" componentName=""
                 parentClasses="public Component, public MessageListener" constructorParams="juce::Array&lt;Image&gt; boardImages"
                 variableInitialisers="" snapPixels="8" snapActive="0" snapShown="1"
                 overlayOpacity="0.330" fixedSize="1" initialWidth="1351" initialHeight="748">
  <BACKGROUND backgroundColour="ffffffff"/>
  <GENERICCOMPONENT name="new board" id="d369032067fd1f6a" memberName="boardComponent"
                    virtualName="" explicitFocusOrder="0" pos="5 5 53.886% 98.262%"
                    class="BoardComponent" params="boardImages, &amp;position"/>
  <TEXTEDITOR name="new text editor" id="dd91023bd06fbf77" memberName="engineOutputText"
              virtualName="" explicitFocusOrder="0" pos="8Rr 8Rr 44.782% 21.658%"
              initialText="Engine output" multiline="1" retKeyStartsLine="0"
              readonly="1" scrollbars="1" caret="0" popupmenu="0"/>
  <VIEWPORT name="new viewport" id="fee84cd0278f227b" memberName="moveListView"
            virtualName="" explicitFocusOrder="0" pos="7Rr 5 44.782% 75.401%"
            vscroll="0" hscroll="0" scrollbarThickness="18" contentType="2"
            jucerFile="MoveListComponent.h" contentClass="" constructorParams=""/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
