#ifndef __JUCE_HEADER_E4DE0C7D386BE276__
#define __JUCE_HEADER_E4DE0C7D386BE276__

#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardPosition/stockfish/position.h"
#include "BoardPosition/stockfish/uci.h"
#include "types.h"

class BoardComponent  : public Component,
                        public MessageListener,
                        public OpenGLRenderer
{
public:
    BoardComponent (juce::Array<Image> boardImages, Stockfish::Position* pos);
    ~BoardComponent();

    void paint (Graphics& g) {};
    void resized();
    void swag () { int a = 3; };

private:
    Image boardImageOriginal;
    Image wPawnImageOriginal, wRookImageOriginal, wKnightImageOriginal, wBishopImageOriginal, wKingImageOriginal, wQueenImageOriginal;
    Image bPawnImageOriginal, bRookImageOriginal, bKnightImageOriginal, bBishopImageOriginal, bKingImageOriginal, bQueenImageOriginal;
    Image boardImage;
    Image wPawnImage, wRookImage, wKnightImage, wBishopImage, wKingImage, wQueenImage;
    Image bPawnImage, bRookImage, bKnightImage, bBishopImage, bKingImage, bQueenImage;

    Stockfish::Position* position;

    int sidePerspective;
    Point<int> mouseDownRankFile, mouseUpRankFile, mouseXY, selectedSquare;
    bool pieceOnBoard[64];
    bool mouseIsDown;
    int squareWidth;

    OpenGLContext openGLContext;
    int renderedFrames;
    void scaleImages ();
    bool resizing;

    void doMove (const Stockfish::Move m);
    Stockfish::Move createMove (Stockfish::Square fromSquare, Stockfish::Square toSquare);
    void mouseDown (const MouseEvent& event) override;
    void mouseUp (const MouseEvent& event) override;
    void mouseDrag (const MouseEvent& event) override;
    // Inherited via MessageListener
    virtual void handleMessage (const Message & message) override;
    // Inherited via OpenGLRenderer
    virtual void newOpenGLContextCreated () override;
    virtual void renderOpenGL () override;
    virtual void openGLContextClosing () override;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (BoardComponent)


};

#endif   // __JUCE_HEADER_E4DE0C7D386BE276__
