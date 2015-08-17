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

#include "BoardTabComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabComponent::BoardTabComponent (juce::Array<Image> boardImages)
{
    //[Constructor_pre] You can add your own custom stuff here..
    //[/Constructor_pre]

    addAndMakeVisible (boardComponent = new BoardComponent (boardImages, &position));
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


    //[UserPreSize]
    moveListView->setViewedComponent (moveListComp = new MoveListComponent(moveListItems));
    //[/UserPreSize]

    setSize (1351, 748);


    //[Constructor] You can add your own custom stuff here..
    //setSize (getBoundsInParent ().getWidth (), getBoundsInParent ().getHeight ());

    Stockfish::Bitboards::init ();
    Stockfish::Position::init ();
    Stockfish::Bitbases::init ();

    position.set ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);

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

    boardComponent->setBounds (5, 5, proportionOfWidth (0.5389f), proportionOfHeight (0.9733f));
    engineOutputText->setBounds (getWidth() - 8 - proportionOfWidth (0.4478f), 728 - 278, proportionOfWidth (0.4478f), 278);
    moveListView->setBounds (getWidth() - 7 - proportionOfWidth (0.4449f), 5, proportionOfWidth (0.4449f), 435);
    //[UserResized] Add your own custom resize handling here..
    moveListView->getViewedComponent()->setBounds (getWidth () - 7 - proportionOfWidth (0.4449f),
                                                 5,
        moveListView->getVerticalScrollBar ()->isVisible () ? proportionOfWidth (0.4449f) - moveListView->getVerticalScrollBar()->getWidth() : proportionOfWidth (0.4449f),
                                                 800);
    //[/UserResized]
}

//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...
void BoardTabComponent::updatePosition()
{
    moveListComp->updateMoveList (moveListItems);
    moveListComp->repaint();
    boardComponent->repaint();
}

void BoardTabComponent::undoMove()
{
    if (moveListItems.size() < 1)
        return;
    position.undo_move (moveListItems.getLast ()->moveNode.move);
    moveListRedoQueue.add (moveListItems.removeAndReturn (moveListItems.size() - 1));
    updatePosition();
}

void BoardTabComponent::redoMove ()
{
    if (moveListRedoQueue.size() < 1)
        return;
    position.do_move (moveListRedoQueue.getLast()->moveNode.move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    moveListItems.add (moveListRedoQueue.removeAndReturn (moveListRedoQueue.size () - 1));
    updatePosition();
}

void BoardTabComponent::handleMessage (const Message & message)
{
    // this method is called by the board when a (half) move has happened, so we should send the info
    // other places.

    if (((GenericMessage*)(&message))->messageType == MSG_MOVEMESSAGE)
    {
        //update movelist
		//juce::String move = Stockfish::UCI::move(((MoveMessage*)(&message))->move, false);
        MoveMessage* moveMessage = ((MoveMessage*)(&message));
		juce::String moveText = moveMessage->moveSAN;

        moveListRedoQueue.clear();
        MoveNode newNode;
        newNode.comments = String::empty;
        newNode.continuation = nullptr;
        newNode.move = moveMessage->move;
        newNode.variation = nullptr;
        String labelText;
        if (position.game_ply () % 2 == 1)
            labelText = std::to_string (position.game_ply () - position.game_ply () / 2) + ". " + moveText, NotificationType::dontSendNotification;
        else
            labelText = moveText + " ";
        moveListItems.add (new MoveListItem (newNode, labelText));
        updatePosition ();
    }
    //txtMoveHist->setText (txtMoveHist->getText () + message);
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
                    virtualName="" explicitFocusOrder="0" pos="5 5 53.886% 97.326%"
                    class="BoardComponent" params="boardImages, &amp;position"/>
  <TEXTEDITOR name="new text editor" id="dd91023bd06fbf77" memberName="engineOutputText"
              virtualName="" explicitFocusOrder="0" pos="8Rr 728r 44.782% 278"
              initialText="Engine output" multiline="1" retKeyStartsLine="0"
              readonly="1" scrollbars="1" caret="0" popupmenu="0"/>
  <VIEWPORT name="new viewport" id="fee84cd0278f227b" memberName="moveListView"
            virtualName="" explicitFocusOrder="0" pos="7Rr 5 44.486% 435"
            vscroll="1" hscroll="1" scrollbarThickness="18" contentType="2"
            jucerFile="MoveListComponent.h" contentClass="" constructorParams=""/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
