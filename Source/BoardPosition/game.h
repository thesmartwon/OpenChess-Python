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
    Stockfish::Position positionAtNode (MoveNode* referenceNode) const;
    void appendMove (MoveNode* referenceNode, MoveNode* toAppend, bool isVariation = false) const;
    void appendMoveToMainline (MoveNode* toAppend, bool isVariation = false);
    InsertionResult insertMoveBefore (MoveNode* referenceNode, MoveNode* toInsert);
    
    bool hasRootNode () const;

private:
    Stockfish::Position rootPosition;
    MoveNode* rootNode;
};