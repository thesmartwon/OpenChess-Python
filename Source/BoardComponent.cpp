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

#include "BoardComponent.h"


//[MiscUserDefs] You can add your own user definitions and misc code here...
//[/MiscUserDefs]

//==============================================================================
BoardComponent::BoardComponent (juce::Array<Image> boardImages, Stockfish::Position* pos)
{
    //[Constructor_pre] You can add your own custom stuff here..
    //[/Constructor_pre]


    //[UserPreSize]
    //[/UserPreSize]

    setSize (886, 766);


    //[Constructor] You can add your own custom stuff here..

    boardImage = boardImages[0];
    piecesImage = boardImages[1];
    wKingImage = boardImages[2];
    wQueenImage = boardImages[3];
    wBishopImage = boardImages[4];
    wKnightImage = boardImages[5];
    wRookImage = boardImages[6];
    wPawnImage = boardImages[7];
    bKingImage = boardImages[8];
    bQueenImage = boardImages[9];
    bBishopImage = boardImages[10];
    bKnightImage = boardImages[11];
    bRookImage = boardImages[12];
    bPawnImage = boardImages[13];
    position = pos;
    sidePerspective = white;
    mouseDownRankFile.addXY (-1, -1);
    mouseUpRankFile.addXY (-1, -1);
    selectedSquare.addXY (-1, -1);
    mouseXY.addXY (-1, -1);
    //a1 is 0, b1 is 2, etc.
    for (int i = 0; i < 64; i++)
        pieceOnBoard[i] = true;
    mouseIsDown = false;

    //openGLContext.attachTo (*this);
    //openGLContext.setContinuousRepainting (true);
    //[/Constructor]
}

BoardComponent::~BoardComponent()
{
    //[Destructor_pre]. You can add your own custom destruction code here..
    //[/Destructor_pre]



    //[Destructor]. You can add your own custom destruction code here..
    openGLContext.detach ();
    //[/Destructor]
}

//==============================================================================
void BoardComponent::paint (Graphics& g)
{
    //[UserPrePaint] Add your own custom painting code here..
    int leftPadding = 0;
    int topPadding = 1;
    bool pieceHovering = false;
    Image myHoveringImage;
    //[/UserPrePaint]

    g.fillAll (Colours::white);

    //[UserPaint] Add your own custom painting code here..
    g.drawImage (boardImage,
        leftPadding, topPadding, 600 + leftPadding, 600 + topPadding,
        leftPadding, topPadding, boardImage.getWidth (), boardImage.getHeight ());
    if (mouseIsDown)
        g.setColour (Colours::green);
    else
        g.setColour (Colours::black);
    //darken dark squares
    g.setColour (Colour::fromRGBA (0x00, 0x00, 0x00, 0x42));
    for (int i = 0; i < 8; ++i)
        for (int j = 0; j < 4; ++j)
        {
            g.fillRect (j * 150 + !(i%2) * 75 + leftPadding, i*75 + topPadding, 75, 75);
        }
    g.setColour (Colours::black);
    //gridlines
    for (int i = 0; i < 7; ++i)
    {
        g.drawLine (75 * (i + 1) + leftPadding, topPadding, 75 * (i + 1) + leftPadding, 600 + topPadding, 2);
        g.drawLine (leftPadding, 75 * (i + 1) + topPadding, 600 + leftPadding, 75 * (i + 1) + topPadding, 2);
    }
    //pieces
    for (Stockfish::Rank ranks = Stockfish::RANK_1; ranks <= Stockfish::RANK_8; ++ranks)
    {
        for (Stockfish::File files = Stockfish::FILE_A; files <= Stockfish::FILE_H; ++files)
        {
            if (position->piece_on (Stockfish::square_of (ranks, files)) != Stockfish::Piece::NO_PIECE)
            {
                Stockfish::Piece piece = position->piece_on (Stockfish::square_of (ranks, files));
                Image myImage;
                if (piece == Stockfish::Piece::W_KING)
                    myImage = wKingImage;
                else if (piece == Stockfish::Piece::W_BISHOP)
                    myImage = wBishopImage;
                else if (piece == Stockfish::Piece::W_KNIGHT)
                    myImage = wKnightImage;
                else if (piece == Stockfish::Piece::W_ROOK)
                    myImage = wRookImage;
                else if (piece == Stockfish::Piece::W_QUEEN)
                    myImage = wQueenImage;
                else if (piece == Stockfish::Piece::W_PAWN)
                    myImage = wPawnImage;
                else if (piece == Stockfish::Piece::B_KING)
                    myImage = bKingImage;
                else if (piece == Stockfish::Piece::B_BISHOP)
                    myImage = bBishopImage;
                else if (piece == Stockfish::Piece::B_KNIGHT)
                    myImage = bKnightImage;
                else if (piece == Stockfish::Piece::B_ROOK)
                    myImage = bRookImage;
                else if (piece == Stockfish::Piece::B_QUEEN)
                    myImage = bQueenImage;
                else if (piece == Stockfish::Piece::B_PAWN)
                    myImage = bPawnImage;

                if (pieceOnBoard[Stockfish::square_of (ranks, files)])
                {
                    g.drawImage (myImage,
                        75 * (files)+leftPadding,
                        sidePerspective == white ? 525 - 75 * (ranks)+topPadding : 75 * (ranks)+topPadding,
                        75,
                        75,
                        0, 0, myImage.getWidth(), myImage.getHeight());
                } else
                {
                    myHoveringImage = myImage;
                    pieceHovering = true;
                }
            }
        }
    }
    //selected square
    g.setColour (Colours::red);
    if (selectedSquare.getX () != -1)
    {
        int rank = 7 - selectedSquare.getX ();
        int file = selectedSquare.getY ();
        //Rectangle<int> r;

        g.drawRect (
            75 * (file)+leftPadding,
            sidePerspective == black ? 525 - 75 * (rank)+topPadding : 75 * (rank)+topPadding,
            75,
            75,
            4);
    }
    //hovering piece
    if (pieceHovering)
    {
        g.drawImage (myHoveringImage,
            mouseXY.getX () - 38,
            mouseXY.getY () - 38,
            75,
            75,
            0, 0, myHoveringImage.getWidth (), myHoveringImage.getHeight ());
        pieceHovering = false;
    }
    //[/UserPaint]
}

void BoardComponent::resized()
{
    //[UserPreResize] Add your own custom resize code here..
    //[/UserPreResize]

    //[UserResized] Add your own custom resize handling here..
    //[/UserResized]
}



//[MiscUserCode] You can add your own definitions of your custom methods or any other code here...

//Stockfish isn't easy going about special moves like castling and promotions. It wants to encode
//those moves with its own special codes and is particular about the way you create them.
Stockfish::Move BoardComponent::createMove (Stockfish::Square fromSquare, Stockfish::Square toSquare)
{
    //castling
    if (fromSquare == Stockfish::Square::SQ_E1 && position->piece_on (Stockfish::Square::SQ_E1) == Stockfish::Piece::W_KING)
    {
        if (toSquare == Stockfish::Square::SQ_G1 || toSquare == Stockfish::Square::SQ_H1) //correct kindside castle
            return Stockfish::make<Stockfish::MoveType::CASTLING> (fromSquare, Stockfish::Square::SQ_H1);
        else if (toSquare == Stockfish::Square::SQ_C1 || toSquare == Stockfish::Square::SQ_B1 || toSquare == Stockfish::Square::SQ_A1) //correct queenside castle
            return Stockfish::make<Stockfish::MoveType::CASTLING> (fromSquare, Stockfish::Square::SQ_A1);
    }
    else if (fromSquare == Stockfish::Square::SQ_E8 && position->piece_on (Stockfish::Square::SQ_E8) == Stockfish::Piece::B_KING)
    {
        if (toSquare == Stockfish::Square::SQ_G8 || toSquare == Stockfish::Square::SQ_H8) //correct kindside castle
            return Stockfish::make<Stockfish::MoveType::CASTLING> (fromSquare, Stockfish::Square::SQ_H8);
        else if (toSquare == Stockfish::Square::SQ_C8 || toSquare == Stockfish::Square::SQ_B8|| toSquare == Stockfish::Square::SQ_A8) //correct queenside castle
            return Stockfish::make<Stockfish::MoveType::CASTLING> (fromSquare, Stockfish::Square::SQ_A8);
    }
    else if (position->piece_on(fromSquare) == Stockfish::Piece::W_PAWN && Stockfish::rank_of(fromSquare) == Stockfish::RANK_5
             && position->piece_on(toSquare) == Stockfish::Piece::NO_PIECE && Stockfish::rank_of(toSquare) == Stockfish::RANK_6
             && (toSquare == Stockfish::Square(fromSquare + 7) || toSquare == Stockfish::Square (fromSquare + 9)))
    {
        //en passant by white
        return Stockfish::make<Stockfish::MoveType::ENPASSANT> (fromSquare, toSquare);
    }
    else if (position->piece_on (fromSquare) == Stockfish::Piece::B_PAWN && Stockfish::rank_of (fromSquare) == Stockfish::RANK_4
        && position->piece_on (toSquare) == Stockfish::Piece::NO_PIECE && Stockfish::rank_of (toSquare) == Stockfish::RANK_3
        && (toSquare == Stockfish::Square (fromSquare - 7) || toSquare == Stockfish::Square (fromSquare - 9)))
    {
        //en passant by black
        return Stockfish::make<Stockfish::MoveType::ENPASSANT> (fromSquare, toSquare);
    }
    else if ((position->piece_on(fromSquare) == Stockfish::Piece::W_PAWN && Stockfish::rank_of (fromSquare) == Stockfish::RANK_7)
         || (position->piece_on (fromSquare) == Stockfish::Piece::B_PAWN && Stockfish::rank_of (fromSquare) == Stockfish::RANK_2))
    {
        //promotion by white or black.
        return Stockfish::make<Stockfish::MoveType::PROMOTION> (fromSquare, toSquare, Stockfish::PieceType::BISHOP);
    }
    return Stockfish::make<Stockfish::MoveType::NORMAL> (fromSquare, toSquare);

}

void BoardComponent::mouseDown (const MouseEvent& event)
{
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        mouseIsDown = true;
        mouseXY.setXY (event.x, event.y);
        if (sidePerspective == white)
            mouseDownRankFile.setXY (7 - event.y / 75, event.x / 75);
        else
            mouseDownRankFile.setXY (event.y / 75, event.x / 75);
        pieceOnBoard[Stockfish::square_of (mouseDownRankFile.getX (), mouseDownRankFile.getY ())] = false;
    }
}

void BoardComponent::mouseUp (const MouseEvent& event)
{
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        mouseXY.setXY (event.x, event.y);
        if (sidePerspective == white)
            mouseUpRankFile.setXY (7 - event.y / 75, event.x / 75);
        else
            mouseUpRankFile.setXY (event.y / 75, event.x / 75);

        Stockfish::Move myMove = Stockfish::Move::MOVE_NONE;
        if (mouseDownRankFile.getX () == mouseUpRankFile.getX () && mouseDownRankFile.getY () == mouseUpRankFile.getY () && selectedSquare.getX () == -1)
        {
            selectedSquare.setXY (mouseUpRankFile.getX (), mouseUpRankFile.getY ());
        }
        //two clicks
        else if (mouseDownRankFile.getX () == mouseUpRankFile.getX () && mouseDownRankFile.getY () == mouseUpRankFile.getY () && selectedSquare.getX () != -1)
        {
            if (mouseDownRankFile.getX () == selectedSquare.getX () && mouseDownRankFile.getY () == selectedSquare.getY ())
                selectedSquare.setXY (-1, -1);
            else
            {
                myMove = createMove (Stockfish::square_of (selectedSquare.getX (), selectedSquare.getY ()),
                    Stockfish::square_of (mouseUpRankFile.getX (), mouseUpRankFile.getY ()));
                doMove (myMove);
            }
        }
        //drag
        else
        {
            myMove = createMove (Stockfish::square_of (mouseDownRankFile.getX (), mouseDownRankFile.getY ()),
                Stockfish::square_of (mouseUpRankFile.getX (), mouseUpRankFile.getY ()));
            doMove (myMove);
        }


        for (int i = 0; i < 64; ++i)
            pieceOnBoard[i] = true;
        repaint ();
        mouseIsDown = false;
    }
}

void BoardComponent::mouseDrag (const MouseEvent & event)
{
    mouseXY.setXY (event.x, event.y);
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        if (event.x < 0 || event.y < 0 || event.x > this->getWidth () || event.y > this->getHeight ())
        {
            for (int i = 0; i < 64; i++)
            {
                pieceOnBoard[i] = true;
            }
            mouseIsDown = false;
        }
        repaint ();
    }
}

void BoardComponent::doMove (const Stockfish::Move move)
{
    if (position->pseudo_legal (move) && position->legal (move, position->pinned_pieces (position->side_to_move ())))
    {
        MoveMessage* mes = new MoveMessage ();
        mes->move = move;
        mes->moveSAN = Stockfish::UCI::move_to_san (*position, move);
        mes->moveUCI = Stockfish::UCI::move (move, false);
        //Stockfish wants a new stateinfo for each move.... /sigh
        position->do_move (move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
        moveList.add (move);


        if (const MessageListener* cm = dynamic_cast<const MessageListener*> (this->getParentComponent ())) //should always be true
            cm->postMessage (mes);
        selectedSquare.setXY (-1, -1);
    }
}

//[/MiscUserCode]


//==============================================================================
#if 0
/*  -- Introjucer information section --

    This is where the Introjucer stores the metadata that describe this GUI layout, so
    make changes in here at your peril!

BEGIN_JUCER_METADATA

<JUCER_COMPONENT documentType="Component" className="BoardComponent" componentName=""
                 parentClasses="public Component, public MouseListener, public MessageListener"
                 constructorParams="juce::Array&lt;Image&gt; boardImages, Stockfish::Position* pos"
                 variableInitialisers="" snapPixels="8" snapActive="1" snapShown="1"
                 overlayOpacity="0.330" fixedSize="0" initialWidth="886" initialHeight="766">
  <BACKGROUND backgroundColour="ffffffff"/>
</JUCER_COMPONENT>

END_JUCER_METADATA
*/
#endif


//[EndFile] You can add extra defines here...
//[/EndFile]
