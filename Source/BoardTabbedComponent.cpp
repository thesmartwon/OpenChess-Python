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

#include "BoardTabbedComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabbedComponent::BoardTabbedComponent (juce::Array<Image> boardImages)
{
    //[Constructor_pre] You can add your own custom stuff here..
    //[/Constructor_pre]

    addAndMakeVisible (cmpBoard = new BoardComponent (boardImages, &position));
    cmpBoard->setName ("new board");

    addAndMakeVisible (txtEngineOutput = new TextEditor ("new text editor"));
    txtEngineOutput->setMultiLine (true);
    txtEngineOutput->setReturnKeyStartsNewLine (false);
    txtEngineOutput->setReadOnly (false);
    txtEngineOutput->setScrollbarsShown (true);
    txtEngineOutput->setCaretVisible (true);
    txtEngineOutput->setPopupMenuEnabled (true);
    txtEngineOutput->setText (TRANS("Engine output"));

    addAndMakeVisible (vwMoveList = new Viewport ("new viewport"));


    //[UserPreSize]
    vwMoveList->setViewedComponent (new MoveListComponent());
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

BoardTabbedComponent::~BoardTabbedComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]

    cmpBoard = nullptr;
    txtEngineOutput = nullptr;
    vwMoveList = nullptr;


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

    cmpBoard->setBounds (5, 5, proportionOfWidth (0.5387f), proportionOfHeight (0.9733f));
    txtEngineOutput->setBounds (getWidth() - 8 - proportionOfWidth (0.4478f), 728 - 278, proportionOfWidth (0.4478f), 278);
    vwMoveList->setBounds (getWidth() - 7 - proportionOfWidth (0.4449f), 5, proportionOfWidth (0.4449f), 435);
    //[UserResized] Add your own custom resize handling here..
    //[/UserResized]
}



//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...
void BoardTabbedComponent::handleMessage (const Message & message)
{
    // this method is called by the board when a (half) move has happened, so we should send the info
    // other placesc.

    if (((GenericMessage*)(&message))->messageType = MSG_MOVEMESSAGE)
    {
        //update movelist
		//juce::String move = Stockfish::UCI::move(((MoveMessage*)(&message))->move, false);
        MoveMessage* moveMessage = ((MoveMessage*)(&message));
		juce::String moveText = moveMessage->moveSAN;

		// TODO: Option to have inline or have with a newline between every ply
       /* std::stringstream stream;
		if (position.game_ply() % 2 == 1)
		{
            stream << txtMoveHist->getText ()
                   << std::right << std::setw (3) << std::setfill (' ')
                   << std::to_string (position.game_ply () - position.game_ply () / 2)
                   << ".";
            stream << std::left << std::setw (8) << std::setfill (' ')
                   << moveText;
			txtMoveHist->setText(stream.str());
		}
        else
        {
            stream << txtMoveHist->getText ()
                   << std::left << std::setw (8) << std::setfill (' ') << moveText << "\n";
            txtMoveHist->setText (stream.str ());
        }*/
        MoveNode newNode;
        newNode.comments = String::empty;
        newNode.continuation = nullptr;
        newNode.move = moveMessage->move;
        newNode.variation = nullptr;
        Label* newLabel = new Label ();
        if (position.game_ply () % 2 == 1)
            newLabel->setText(std::to_string (position.game_ply () - position.game_ply () / 2) + "." + moveText, NotificationType::dontSendNotification);
        else
            newLabel->setText (moveText, NotificationType::dontSendNotification);
        newLabel->setTopLeftPosition (865 - 20, 20);
        this->toFront (newLabel);
        newLabel->setEditable (false);
        newLabel->setBounds (865 - 20, 20, 100, 100);
        newLabel->addMouseListener (this, false);
        addAndMakeVisible (newLabel);
        MoveListItem* newMoveListItem = new MoveListItem (newNode, newLabel);
        moveListLabels.add (newMoveListItem);
        repaint ();
        //update engine
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

<JUCER_COMPONENT documentType="Component" className="BoardTabbedComponent" componentName=""
                 parentClasses="public Component, public MessageListener" constructorParams="juce::Array&lt;Image&gt; boardImages"
                 variableInitialisers="" snapPixels="8" snapActive="0" snapShown="1"
                 overlayOpacity="0.330" fixedSize="1" initialWidth="1351" initialHeight="748">
  <BACKGROUND backgroundColour="ffffffff"/>
  <GENERICCOMPONENT name="new board" id="d369032067fd1f6a" memberName="cmpBoard"
                    virtualName="" explicitFocusOrder="0" pos="5 5 53.886% 97.326%"
                    class="BoardComponent" params="boardImages, &amp;position"/>
  <TEXTEDITOR name="new text editor" id="dd91023bd06fbf77" memberName="txtEngineOutput"
              virtualName="" explicitFocusOrder="0" pos="8Rr 728r 44.782% 278"
              initialText="Engine output" multiline="1" retKeyStartsLine="0"
              readonly="0" scrollbars="1" caret="1" popupmenu="1"/>
  <VIEWPORT name="new viewport" id="fee84cd0278f227b" memberName="vwMoveList"
            virtualName="" explicitFocusOrder="0" pos="7Rr 5 44.486% 435"
            vscroll="1" hscroll="1" scrollbarThickness="18" contentType="2"
            jucerFile="MoveListComponent.h" contentClass="" constructorParams=""/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
