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

class Game
{
public:
    Game ();
    Game (const juce::String startingFEN);

    //==============================================================================
    /**
    If node doesn't exist will return rootPosition
    */
    void appendMove (MoveNode* referenceNode, MoveNode* toAppend, bool isVariation = false);
    void appendMoveToMainline (MoveNode* toAppend, bool isVariation = false);
    bool insertMoveBefore (MoveNode* referenceNode, MoveNode* toInsert);
    
    bool hasRootNode () const;
    MoveNode* getCurrentlyViewedNode () const;
    void setCurrentlyViewedNode (MoveNode* nodeToView);

    Stockfish::Position positionAtNode (MoveNode* referenceNode) const;
    Stockfish::Position getCurrentlyViewedPosition () const;

private:
    Stockfish::Position rootPosition;
    MoveNode* rootNode;
    MoveNode* currentlyViewedNode;

};