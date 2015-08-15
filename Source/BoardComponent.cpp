#include "BoardComponent.h"

BoardComponent::BoardComponent (juce::Array<Image> boardImages, Stockfish::Position* pos)
{

    setSize (728, 728);


    boardImage = boardImages[0];
    wKingImage = boardImages[1];
    wQueenImage = boardImages[2];
    wBishopImage = boardImages[3];
    wKnightImage = boardImages[4];
    wRookImage = boardImages[5];
    wPawnImage = boardImages[6];
    bKingImage = boardImages[7];
    bQueenImage = boardImages[8];
    bBishopImage = boardImages[9];
    bKnightImage = boardImages[10];
    bRookImage = boardImages[11];
    bPawnImage = boardImages[12];
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
    squareWidth = getWidth() / 8;

    setOpaque (true);
    //openGLContext.setRenderer (this);
    //openGLContext.setContinuousRepainting (true);
    //openGLContext.setComponentPaintingEnabled (true);
    openGLContext.attachTo (*this);
}

BoardComponent::~BoardComponent()
{
    if (openGLContext.getTargetComponent() == this)
        openGLContext.detach ();
}


void BoardComponent::paint (Graphics& g)
{
    bool pieceHovering = false;
    Image myHoveringImage;

    //the background
    g.drawImage (boardImage,
        0, 0, getWidth(), getHeight(),
        0, 0, boardImage.getWidth (), boardImage.getHeight ());
    
    //shading the darker squares
    g.setColour (Colour::fromRGBA (0x00, 0x00, 0x00, 0x42));
    for (int i = 0; i < 8; ++i)
        for (int j = 0; j < 4; ++j)
        {
            g.fillRect (j * squareWidth * 2 + !(i%2) * squareWidth, i*squareWidth, squareWidth, squareWidth);
        }
    g.setColour (Colours::black);
    //gridlines
    for (int i = 0; i < 7; ++i)
    {
        g.drawLine (squareWidth * (i + 1), 0, squareWidth * (i + 1), getWidth(), 2);
        g.drawLine (0, squareWidth * (i + 1), getWidth(), squareWidth * (i + 1), 2);
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
                        squareWidth * (files),
                        sidePerspective == white ? squareWidth * 7 - squareWidth * (ranks) : squareWidth * (ranks),
                        squareWidth,
                        squareWidth,
                        0, 0, myImage.getWidth(), myImage.getHeight());
                } else
                {
                    myHoveringImage = myImage;
                    pieceHovering = true;
                }
            }
        }
    }
    //selected square outline
    g.setColour (Colours::red);
    if (selectedSquare.getX () != -1)
    {
        int rank = 7 - selectedSquare.getX ();
        int file = selectedSquare.getY ();

        g.drawRect (
            squareWidth * (file),
            sidePerspective == black ? squareWidth * 7 - squareWidth * (rank): squareWidth * (rank),
            squareWidth,
            squareWidth,
            4);
    }
    //hovering piece
    if (pieceHovering)
    {
        g.drawImage (myHoveringImage,
            mouseXY.getX () - squareWidth / 2,
            mouseXY.getY () - squareWidth / 2,
            squareWidth,
            squareWidth,
            0, 0, myHoveringImage.getWidth (), myHoveringImage.getHeight ());
        pieceHovering = false;
    }
    //for debugging
    g.setColour (Colours::red);
    g.drawRect (0,0,getWidth(),getHeight(), 2);
}

void BoardComponent::resized()
{
    if (getHeight() > getWidth ())
    {
        juce::Rectangle<int> newBounds = getBounds();
        newBounds.setHeight (getWidth() - getWidth () % 8);
        setBounds (newBounds);
        squareWidth = getWidth() / 8;
    }
    else
    {
        juce::Rectangle<int> newBounds = getBounds();
        newBounds.setWidth (getHeight() - getHeight() % 8);
        setBounds (newBounds);
        squareWidth = getHeight() / 8;
    }
}


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
            mouseDownRankFile.setXY (7 - event.y / squareWidth, event.x / squareWidth);
        else
            mouseDownRankFile.setXY (event.y / squareWidth, event.x / squareWidth);
        pieceOnBoard[Stockfish::square_of (mouseDownRankFile.getX (), mouseDownRankFile.getY ())] = false;
    }
}

void BoardComponent::mouseUp (const MouseEvent& event)
{
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        mouseXY.setXY (event.x, event.y);
        if (sidePerspective == white)
            mouseUpRankFile.setXY (7 - event.y / squareWidth, event.x / squareWidth);
        else
            mouseUpRankFile.setXY (event.y / squareWidth, event.x / squareWidth);

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

void BoardComponent::handleMessage (const Message & message)
{
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

        if (const MessageListener* cm = dynamic_cast<const MessageListener*> (this->getParentComponent ())) //should always be true
            cm->postMessage (mes);
        selectedSquare.setXY (-1, -1);
    }
}