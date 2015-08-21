#pragma once
#include "../../JuceLibraryCode/JuceHeader.h"
#include "stockfish/position.h"
#include "../types.h"

struct MoveNode
{
    MoveNode* parent;
    MoveNode* continuation;
    MoveNode* variation;
    Stockfish::Move move;
    juce::String moveLabelText;
    juce::String comments;
    MoveNode (){ parent = continuation = variation = nullptr; move = Stockfish::Move::MOVE_NONE; comments = String::empty; }
    MoveNode (const MoveNode* other)
    {
        this->parent = other->parent;
        this->continuation = other->continuation;
        this->variation = other->variation;
        this->move = other->move;
        this->moveLabelText = String (other->moveLabelText);
        this->comments = String (other->comments);
    };
    bool MoveNode::operator==(MoveNode &rhs)
    {
        if (this->continuation == rhs.continuation && this->variation == rhs.variation
            && this->move == rhs.move && this->comments == rhs.comments && this->parent == rhs.parent)
            return true;
        return false;
    }
};

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
	void doMainlineMove(Stockfish::Move m, juce::String moveSAN, bool isRedo = false);
	void undoMove();
	void redoMove();
    
    MoveNode* getRootNode () const;
    MoveNode* getCurrentlyViewedNode () const;
    void setCurrentlyViewedNode (MoveNode* nodeToView);

    Stockfish::Position getCurrentlyViewedPosition () const;

private:
    Stockfish::Position rootPosition, currentlyViewedPosition;
    MoveNode* rootNode;
    MoveNode* currentlyViewedNode;
	juce::Array<MoveNode*> redoStack;

};