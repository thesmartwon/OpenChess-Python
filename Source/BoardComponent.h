#ifndef __JUCE_HEADER_E4DE0C7D386BE276__
#define __JUCE_HEADER_E4DE0C7D386BE276__

#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardPosition/stockfish/position.h"
#include "BoardPosition/stockfish/uci.h"
#include "BoardPosition/game.h"
#include "types.h"

class BoardComponent  : public Component,
                        public ChangeBroadcaster,
                        public OpenGLRenderer
{
public:
    BoardComponent (juce::Array<Image> boardImages, Game* game);
    ~BoardComponent();

    MoveMessage* getLastMoveMessage ();

    void paint (Graphics& g) {};
    void resized();

private:
    Image boardImageOriginal;
    Image wPawnImageOriginal, wRookImageOriginal, wKnightImageOriginal, wBishopImageOriginal, wKingImageOriginal, wQueenImageOriginal;
    Image bPawnImageOriginal, bRookImageOriginal, bKnightImageOriginal, bBishopImageOriginal, bKingImageOriginal, bQueenImageOriginal;
    Image boardImage;
    Image wPawnImage, wRookImage, wKnightImage, wBishopImage, wKingImage, wQueenImage;
    Image bPawnImage, bRookImage, bKnightImage, bBishopImage, bKingImage, bQueenImage;

    Game* activeGame;
    MoveMessage lastMoveMessage;

    int sidePerspective;
    Point<int> mouseDownRankFile, mouseUpRankFile, mouseXY, selectedSquare;
    bool pieceOnBoard[64];
    bool mouseIsDown;
    int squareWidth;

    OpenGLContext openGLContext;
    String lastMeasuredFPS;
    void scaleImages ();
    bool resizing;

    void sendMove (const Stockfish::Move m);
    Stockfish::Move createMove (Stockfish::Square fromSquare, Stockfish::Square toSquare);
    void mouseDown (const MouseEvent& event) override;
    void mouseUp (const MouseEvent& event) override;
    void mouseDrag (const MouseEvent& event) override;
    // Inherited via OpenGLRenderer
    virtual void newOpenGLContextCreated () override;
    virtual void renderOpenGL () override;
    virtual void openGLContextClosing () override;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (BoardComponent)


};

#endif   // __JUCE_HEADER_E4DE0C7D386BE276__
