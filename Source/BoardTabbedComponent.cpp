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

//[Headers] You can add your own extra header files here...
//[/Headers]

#include "BoardTabbedComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardTabbedComponent::BoardTabbedComponent (juce::Array<Image> boardImages)
{
    addAndMakeVisible (txtMoveHist = new TextEditor ("move history text editor"));
    txtMoveHist->setTooltip (TRANS("Move History"));
    txtMoveHist->setMultiLine (true);
    txtMoveHist->setReturnKeyStartsNewLine (false);
    txtMoveHist->setReadOnly (false);
    txtMoveHist->setScrollbarsShown (true);
    txtMoveHist->setCaretVisible (true);
    txtMoveHist->setPopupMenuEnabled (true);
    txtMoveHist->setText (TRANS(""));

    addAndMakeVisible (cmpBoard = new BoardComponent (boardImages, &position));
    cmpBoard->setName ("new board");

    addAndMakeVisible (txtEngineOutput = new TextEditor ("new text editor"));
    txtEngineOutput->setMultiLine (false);
    txtEngineOutput->setReturnKeyStartsNewLine (false);
    txtEngineOutput->setReadOnly (false);
    txtEngineOutput->setScrollbarsShown (true);
    txtEngineOutput->setCaretVisible (true);
    txtEngineOutput->setPopupMenuEnabled (true);
    txtEngineOutput->setText (TRANS("Engine output"));

    //[UserPreSize]
    //[/UserPreSize]

    setSize (600, 400);


    //[Constructor] You can add your own custom stuff here..
    setSize (865, 712);

    Stockfish::Bitboards::init ();
    Stockfish::Position::init ();
    Stockfish::Bitbases::init ();

    position.st = (Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo));
    position.set ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);
    //Move m (AGChess::e2, AGChess::e4);      // e2, e4 are defined in Square.h
    //position.make (m);          // Make the move
    //cmpBoard->setBoardPosition (position);
    //[/Constructor]
}

BoardTabbedComponent::~BoardTabbedComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]

    txtMoveHist = nullptr;
    cmpBoard = nullptr;
    txtEngineOutput = nullptr;


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

    txtMoveHist->setBounds (616, 7, 257, 600);
    cmpBoard->setBounds (8, 6, 600, 600);
    txtEngineOutput->setBounds (8, 615, 864, 103);
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
		juce::String a = Stockfish::UCI::movePGN (moveMessage->move, *moveMessage->pos, false);

		// TODO: Option to have inline or have with a newline between every ply
		if (((MoveMessage*)(&message))->pos->game_ply() % 2 == 1)
		{
			txtMoveHist->setText(txtMoveHist->getText() + std::to_string(moveMessage->pos->game_ply() - moveMessage->pos->game_ply() / 2) + ".  ");
			txtMoveHist->setText(txtMoveHist->getText() + a + "    ");
		}
		else
			txtMoveHist->setText(txtMoveHist->getText() + a + "\n");

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
                 parentClasses="public Component" constructorParams="" variableInitialisers=""
                 snapPixels="8" snapActive="1" snapShown="1" overlayOpacity="0.330"
                 fixedSize="0" initialWidth="600" initialHeight="400">
  <BACKGROUND backgroundColour="ffffffff"/>
  <TEXTEDITOR name="move history text editor" id="bd474a33f39524" memberName="txtMoveHist"
              virtualName="" explicitFocusOrder="0" pos="616 7 257 600" tooltip="Move History"
              initialText="1. e4  2. e5  3. Nf3  4. Nf6  5. Nxe5" multiline="0"
              retKeyStartsLine="0" readonly="0" scrollbars="1" caret="1" popupmenu="1"/>
  <GENERICCOMPONENT name="new board" id="d369032067fd1f6a" memberName="cmpBoard"
                    virtualName="" explicitFocusOrder="0" pos="8 6 600 600" class="BoardComponent"
                    params=""/>
  <TEXTEDITOR name="new text editor" id="dd91023bd06fbf77" memberName="txtEngineOutput"
              virtualName="" explicitFocusOrder="0" pos="8 615 864 103" initialText="Engine output"
              multiline="0" retKeyStartsLine="0" readonly="0" scrollbars="1"
              caret="1" popupmenu="1"/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
