#include "stdafx.h"
#include "BoardComponent.h"

using namespace Stockfish;

class PiecesMenuComponent : public PopupMenu::CustomComponent
{
public:
    PiecesMenuComponent (Image pieceImage, int squareWidth)
    {
        this->pieceImage = pieceImage;
        this->squareWidth = squareWidth;
    }

    void getIdealSize (int& idealWidth, int& idealHeight) override
    {
        idealWidth = squareWidth - 4;
        idealHeight = squareWidth;
    }

    void paint (Graphics& g) override
    {
        g.fillAll (Colours::black.withAlpha (0.3f));

        g.drawImage (pieceImage, 0, 0, squareWidth - 4, squareWidth, 0, 0, pieceImage.getWidth (), pieceImage.getHeight ());

        //g.setColour (Colours::black);
        //g.drawEllipse (getLocalBounds ().toFloat(), 1);
    }

private:
    Image pieceImage;
    int squareWidth;
};

BoardComponent::BoardComponent (juce::Array<Image> boardImages, Game* game)
{
    setOpaque (true);

    int a = boardImages.size ();
    activeGame = game;

    squareWidth = getWidth() / 8;
    boardImageOriginal = boardImages[0];
    wKingImageOriginal = boardImages[1];
    wQueenImageOriginal = boardImages[2];
    wBishopImageOriginal = boardImages[3];
    wKnightImageOriginal = boardImages[4];
    wRookImageOriginal = boardImages[5];
    wPawnImageOriginal = boardImages[6];
    bKingImageOriginal = boardImages[7];
    bQueenImageOriginal = boardImages[8];
    bBishopImageOriginal = boardImages[9];
    bKnightImageOriginal = boardImages[10];
    bRookImageOriginal = boardImages[11];
    bPawnImageOriginal = boardImages[12];

    setSize (728, 728);

    boardImage = boardImages[13];
    wKingImage = boardImages[14];
    wQueenImage = boardImages[15];
    wBishopImage = boardImages[16];
    wKnightImage = boardImages[17];
    wRookImage = boardImages[18];
    wPawnImage = boardImages[19];
    bKingImage = boardImages[20];
    bQueenImage = boardImages[21];
    bBishopImage = boardImages[22];
    bKnightImage = boardImages[23];
    bRookImage = boardImages[24];
    bPawnImage = boardImages[25];

    sidePerspective = WHITE;
    mouseDownRankFile.addXY (-1, -1);
    mouseUpRankFile.addXY (-1, -1);
    selectedSquare.addXY (-1, -1);
    mouseXY.addXY (-1, -1);
    //a1 is 0, b1 is 2, etc.
    for (int i = 0; i < 64; i++)
        pieceOnBoard[i] = true;
    mouseIsDown = resizing = false;
    lastMeasuredFPS = "0";
    lastMoveMessage.move = Move::MOVE_NONE;
    lastMoveMessage.moveSAN = String::empty;
    lastMoveMessage.moveUCI = String::empty;

    openGLContext.setRenderer (this);
    openGLContext.attachTo (*this);
    openGLContext.setContinuousRepainting (true);
    setSize (728, 728);
}

BoardComponent::~BoardComponent()
{
    if (openGLContext.getTargetComponent () == this)
        openGLContext.detach ();
}

MoveMessage* BoardComponent::getLastMoveMessage ()
{
    return &lastMoveMessage;
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
    resizing = true;
}

//Stockfish isn't easy going about special moves like castling and promotions. It wants to encode
//those moves with its own special codes and is particular about the way you create them.
Move BoardComponent::createMove (Square fromSquare, Square toSquare)
{
    //castling
    if (fromSquare == Square::SQ_E1 && activeGame->piece_on (Square::SQ_E1) == Piece::W_KING)
    {
        if (toSquare == Square::SQ_G1 || toSquare == Square::SQ_H1) //correct kindside castle
            return make<MoveType::CASTLING> (fromSquare, Square::SQ_H1);
        else if (toSquare == Square::SQ_C1 || toSquare == Square::SQ_B1 || toSquare == Square::SQ_A1) //correct queenside castle
            return make<MoveType::CASTLING> (fromSquare, Square::SQ_A1);
    }
    else if (fromSquare == Square::SQ_E8 && activeGame->piece_on (Square::SQ_E8) == Piece::B_KING)
    {
        if (toSquare == Square::SQ_G8 || toSquare == Square::SQ_H8) //correct kindside castle
            return make<MoveType::CASTLING> (fromSquare, Square::SQ_H8);
        else if (toSquare == Square::SQ_C8 || toSquare == Square::SQ_B8|| toSquare == Square::SQ_A8) //correct queenside castle
            return make<MoveType::CASTLING> (fromSquare, Square::SQ_A8);
    }
    else if (activeGame->piece_on(fromSquare) == Piece::W_PAWN && rank_of(fromSquare) == RANK_5
             && activeGame->piece_on(toSquare) == Piece::NO_PIECE && rank_of(toSquare) == RANK_6
             && (toSquare == Square(fromSquare + 7) || toSquare == Square (fromSquare + 9)))
    {
        //en passant by white
        return make<MoveType::ENPASSANT> (fromSquare, toSquare);
    }
    else if (activeGame->piece_on (fromSquare) == Piece::B_PAWN && rank_of (fromSquare) == RANK_4
        && activeGame->piece_on (toSquare) == Piece::NO_PIECE && rank_of (toSquare) == RANK_3
        && (toSquare == Square (fromSquare - 7) || toSquare == Square (fromSquare - 9)))
    {
        //en passant by black
        return make<MoveType::ENPASSANT> (fromSquare, toSquare);
    }
    else if ((activeGame->piece_on(fromSquare) == Piece::W_PAWN && rank_of (fromSquare) == RANK_7)
         || (activeGame->piece_on (fromSquare) == Piece::B_PAWN && rank_of (fromSquare) == RANK_2))
    {
        //promotion by white or black.
        PopupMenu m;
        if (activeGame->side_to_move () == WHITE)
        {
            m.addCustomItem (PieceType::QUEEN, new PiecesMenuComponent (wQueenImage, squareWidth));
            m.addCustomItem (PieceType::KNIGHT, new PiecesMenuComponent (wKnightImage, squareWidth));
            m.addCustomItem (PieceType::ROOK, new PiecesMenuComponent (wRookImage, squareWidth));
            m.addCustomItem (PieceType::BISHOP, new PiecesMenuComponent (wBishopImage, squareWidth));
        }
        else
        {
            m.addCustomItem (PieceType::BISHOP, new PiecesMenuComponent (bBishopImage, squareWidth));
            m.addCustomItem (PieceType::ROOK, new PiecesMenuComponent (bRookImage, squareWidth));
            m.addCustomItem (PieceType::KNIGHT, new PiecesMenuComponent (bKnightImage, squareWidth));
            m.addCustomItem (PieceType::QUEEN, new PiecesMenuComponent (bQueenImage, squareWidth));
        }
        int popupY = getScreenBounds ().getY ();
        popupY += activeGame->side_to_move() == WHITE ? 0 : 8 * squareWidth;
        PieceType p = PieceType(m.showAt(juce::Rectangle<int>(getScreenBounds().getX() + squareWidth * (file_of (toSquare)),
                                                                                    popupY,
                                                                                    0,
                                                                                    0)));
        return make<MoveType::PROMOTION> (fromSquare, toSquare, p);
    }
    return make<MoveType::NORMAL> (fromSquare, toSquare);

}

void BoardComponent::mouseDown (const MouseEvent& event)
{
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        mouseIsDown = true;
        mouseXY.setXY (event.x, event.y);
        if (sidePerspective == WHITE)
            mouseDownRankFile.setXY (7 - event.y / squareWidth, event.x / squareWidth);
        else
            mouseDownRankFile.setXY (event.y / squareWidth, event.x / squareWidth);
        pieceOnBoard[square_of (mouseDownRankFile.getX (), mouseDownRankFile.getY ())] = false;
    }
}

void BoardComponent::mouseUp (const MouseEvent& event)
{
    if (event.mods == juce::ModifierKeys::leftButtonModifier)
    {
        mouseXY.setXY (event.x, event.y);
        if (sidePerspective == WHITE)
            mouseUpRankFile.setXY (7 - event.y / squareWidth, event.x / squareWidth);
        else
            mouseUpRankFile.setXY (event.y / squareWidth, event.x / squareWidth);

        Move myMove = Move::MOVE_NONE;
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
                myMove = createMove (square_of (selectedSquare.getX (), selectedSquare.getY ()),
                                     square_of (mouseUpRankFile.getX (), mouseUpRankFile.getY ()));
                sendMove (myMove);
            }
        }
        //drag
        else
        {
            myMove = createMove (square_of (mouseDownRankFile.getX (), mouseDownRankFile.getY ()),
                                 square_of (mouseUpRankFile.getX (), mouseUpRankFile.getY ()));
            sendMove (myMove);
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

void BoardComponent::scaleImages ()
{
    // we only want to resize our pieces once, constant resizing every frame is expensive
    if (!boardImage.isNull () && !resizing && boardImage.getWidth () != getWidth () && getWidth () != 0)
        boardImage = boardImageOriginal.rescaled (getWidth (), getHeight ());
    if (!wKingImage.isNull () && !resizing && wKingImage.getWidth () != squareWidth && squareWidth != 0)
        wKingImage = wKingImageOriginal.rescaled (squareWidth, squareWidth);
    if (!wQueenImage.isNull () && !resizing && wQueenImage.getWidth () != squareWidth && squareWidth != 0)
        wQueenImage = wQueenImageOriginal.rescaled (squareWidth, squareWidth);
    if (!wBishopImage.isNull () && !resizing && wBishopImage.getWidth () != squareWidth && squareWidth != 0)
        wBishopImage = wBishopImageOriginal.rescaled (squareWidth, squareWidth);
    if (!wKnightImage.isNull () && !resizing && wKnightImage.getWidth () != squareWidth && squareWidth != 0)
        wKnightImage = wKnightImageOriginal.rescaled (squareWidth, squareWidth);
    if (!wRookImage.isNull () && !resizing && wRookImage.getWidth () != squareWidth && squareWidth != 0)
        wRookImage = wRookImageOriginal.rescaled (squareWidth, squareWidth);
    if (!wPawnImage.isNull () && !resizing && wPawnImage.getWidth () != squareWidth && squareWidth != 0)
        wPawnImage = wPawnImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bKingImage.isNull () && !resizing && bKingImage.getWidth () != squareWidth && squareWidth != 0)
        bKingImage = bKingImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bQueenImage.isNull () && !resizing && bQueenImage.getWidth () != squareWidth && squareWidth != 0)
        bQueenImage = bQueenImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bBishopImage.isNull () && !resizing && bBishopImage.getWidth () != squareWidth && squareWidth != 0)
        bBishopImage = bBishopImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bKnightImage.isNull () && !resizing && bKnightImage.getWidth () != squareWidth && squareWidth != 0)
        bKnightImage = bKnightImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bRookImage.isNull () && !resizing && bRookImage.getWidth () != squareWidth && squareWidth != 0)
        bRookImage = bRookImageOriginal.rescaled (squareWidth, squareWidth);
    if (!bPawnImage.isNull () && !resizing && bPawnImage.getWidth () != squareWidth && squareWidth != 0)
        bPawnImage = bPawnImageOriginal.rescaled (squareWidth, squareWidth);
}

void BoardComponent::newOpenGLContextCreated()
{
    scaleImages ();
}

void BoardComponent::renderOpenGL()
{
    jassert (OpenGLHelpers::isContextActive ());
    // Create an OpenGLGraphicsContext that will draw into this GL window..
    const float desktopScale = (float)openGLContext.getRenderingScale ();
    ScopedPointer<juce::LowLevelGraphicsContext> glRenderer (createOpenGLGraphicsContext (openGLContext,
                                                                                    roundToInt (desktopScale * getWidth ()),
                                                                                    roundToInt (desktopScale * getHeight ())));

    if (glRenderer != nullptr)
    {
        Graphics g (*glRenderer);
        scaleImages();
        //the background
        g.drawImage (boardImage,
            0, 0, getWidth (), getHeight (),
            0, 0, boardImage.getWidth (), boardImage.getHeight ());

        //shading the darker squares
        g.setColour (Colour::fromRGBA (0x00, 0x00, 0x00, 0x42));
        for (int i = 0; i < 8; ++i)
            for (int j = 0; j < 4; ++j)
            {
                g.fillRect (j * squareWidth * 2 + !(i % 2) * squareWidth, i*squareWidth, squareWidth, squareWidth);
            }
        g.setColour (Colours::black);

        //gridlines
        for (int i = 0; i < 7; ++i)
        {
            g.drawLine (squareWidth * (i + 1), 0, squareWidth * (i + 1), getWidth (), 2);
            g.drawLine (0, squareWidth * (i + 1), getWidth (), squareWidth * (i + 1), 2);
        }

        //pieces
        bool pieceHovering = false;
        Image myHoveringImage;
        for (Rank ranks = RANK_1; ranks <= RANK_8; ++ranks)
        {
            for (Stockfish::File files = FILE_A; files <= FILE_H; ++files)
            {
                Piece piece = activeGame->piece_on (square_of (ranks, files));
                if (piece != Piece::NO_PIECE)
                {
                    Image myImage;
                    if (piece == Piece::W_KING)
                        myImage = wKingImage;
                    else if (piece == Piece::W_BISHOP)
                        myImage = wBishopImage;
                    else if (piece == Piece::W_KNIGHT)
                        myImage = wKnightImage;
                    else if (piece == Piece::W_ROOK)
                        myImage = wRookImage;
                    else if (piece == Piece::W_QUEEN)
                        myImage = wQueenImage;
                    else if (piece == Piece::W_PAWN)
                        myImage = wPawnImage;
                    else if (piece == Piece::B_KING)
                        myImage = bKingImage;
                    else if (piece == Piece::B_BISHOP)
                        myImage = bBishopImage;
                    else if (piece == Piece::B_KNIGHT)
                        myImage = bKnightImage;
                    else if (piece == Piece::B_ROOK)
                        myImage = bRookImage;
                    else if (piece == Piece::B_QUEEN)
                        myImage = bQueenImage;
                    else if (piece == Piece::B_PAWN)
                        myImage = bPawnImage;

                    if (pieceOnBoard[square_of (ranks, files)])
                    {
                        g.drawImage (myImage,
                            squareWidth * (files),
                            sidePerspective == WHITE ? squareWidth * 7 - squareWidth * (ranks) : squareWidth * (ranks),
                            squareWidth,
                            squareWidth,
                            0, 0, myImage.getWidth (), myImage.getHeight ());
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
                sidePerspective == BLACK ? squareWidth * 7 - squareWidth * (rank) : squareWidth * (rank),
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
        resizing = false;
        //for debugging
        g.setColour (Colours::red);
        g.drawRect (0, 0, getWidth (), getHeight (), 2);
        static DWORD LastFPSTime = GetTickCount (), LastFrameTime = LastFPSTime;
        static int FPS = 0;

        DWORD Time = GetTickCount () * 0.9 + LastFrameTime * 0.1;
        LastFrameTime = Time;
        if (Time - LastFPSTime > 1000)
        {
            lastMeasuredFPS = String (FPS);
            LastFPSTime = Time;
            FPS = 0;
        } else
            FPS++;
        g.drawText (String (lastMeasuredFPS), 5, 5, 200, 20, Justification::left);

    }
}

void BoardComponent::openGLContextClosing()
{
}

void BoardComponent::sendMove (const Move move)
{
    if (activeGame->is_legal(move))
    {
        lastMoveMessage.move = move;
        lastMoveMessage.moveSAN = activeGame->getMoveSAN(move);
        lastMoveMessage.moveUCI = activeGame->getMoveUCI(move);

        // we do this here for animation and speed's sake
        activeGame->doMainlineMove (move, lastMoveMessage.moveSAN);
        activeGame->isStalement();
        activeGame->isDraw();

        // tell the boardTabComponenet we have moved
        sendSynchronousChangeMessage (); // being synchronous allows for extra speed 

        selectedSquare.setXY (-1, -1);
    }
}