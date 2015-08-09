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

#ifndef __JUCE_HEADER_E4DE0C7D386BE276__
#define __JUCE_HEADER_E4DE0C7D386BE276__

//[Headers]     -- You can add your own extra header files here --
#include "JuceHeader.h"
#include "BoardPosition/stockfish/position.h"
#include "BoardPosition/stockfish/uci.h"
#include "types.h"
//[/Headers]



//==============================================================================
/**
                                                                    //[Comments]
    An auto-generated component, created by the Introjucer.

    Describe your class and how it works here!
                                                                    //[/Comments]
*/
class BoardComponent  : public Component,
                        public MouseListener,
                        public MessageListener
{
public:
    //==============================================================================
    BoardComponent (juce::Array<Image> boardImages, Stockfish::Position* p);
    ~BoardComponent ();

    //==============================================================================
    //[UserMethods]     -- You can add your own custom methods in this section.
    enum PieceColor
    {
        white = 0,
        black = 1,
        noColor = 2
    };
    void doMove (const Stockfish::Move m);
    Stockfish::Move createMove (Stockfish::Square fromSquare, Stockfish::Square toSquare);
    //[/UserMethods]

    void paint (Graphics& g);
    void resized();



private:
    //[UserVariables]   -- You can add your own custom variables in this section.
    Image boardImage, piecesImage;
    Image wPawnImage, wRookImage, wKnightImage, wBishopImage, wKingImage, wQueenImage;
    Image bPawnImage, bRookImage, bKnightImage, bBishopImage, bKingImage, bQueenImage;

    Stockfish::Position* position;
    juce::Array<Stockfish::Move> moveList;
    int sidePerspective;
    Point<int> mouseDownRankFile, mouseUpRankFile, mouseXY, selectedSquare;
    bool pieceOnBoard[64];
    bool mouseIsDown;

    void mouseDown (const MouseEvent& event) override;
    void mouseUp (const MouseEvent& event) override;
    void mouseDrag (const MouseEvent& event) override;

    OpenGLContext openGLContext;

    virtual void handleMessage (const Message & message) override {};
    //[/UserVariables]

    //==============================================================================


    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (BoardComponent)

};

//[EndFile] You can add extra defines here...
//[/EndFile]

#endif   // __JUCE_HEADER_E4DE0C7D386BE276__
