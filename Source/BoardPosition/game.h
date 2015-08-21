#pragma once
#include "../../JuceLibraryCode/JuceHeader.h"
#include "stockfish/position.h"
#include "../types.h"
#include <stack>

struct InsertionResult
{
    MoveNode* continuationBrokenNode;
    juce::Array<MoveNode*> variationBrokenNodes;
};

//==============================================================================
/**
The game class is composed of moveNodes in a simple binary tree.
One side represents variations, the other the mainline.
*/
class Game
{
public:
    Game ();
    Game (const juce::String startingFEN);

    //==============================================================================
    /**
    If node doesn't exist will return rootPosition
    */
    void appendNode (MoveNode* referenceNode, MoveNode* toAppend, bool isVariation = false);
    void appendNodeToMainline (MoveNode* toAppend, bool isVariation = false);
    bool insertNodeBefore (MoveNode* referenceNode, MoveNode* toInsert);
	void doMainlineMove(Stockfish::Move m, juce::String moveSAN);
	void undoMove();
	void redoMove();
    
    MoveNode* getCurrentlyViewedNode () const;
    void setCurrentlyViewedNode (MoveNode* nodeToView);

    Stockfish::Position getCurrentlyViewedPosition () const;

private:
    Stockfish::Position rootPosition, currentlyViewedPosition;
    MoveNode* rootNode;
    MoveNode* currentlyViewedNode;
	juce::Array<MoveNode*> redoStack;

};