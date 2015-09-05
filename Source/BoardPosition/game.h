#pragma once
#include "../../JuceLibraryCode/JuceHeader.h"
#include "stockfish/position.h"
#include "../types.h"

//struct MoveNode
//{
//    MoveNode* parent;
//    MoveNode* continuation;
//    MoveNode* variation;
//    Stockfish::Move move;
//    juce::String moveLabelText;
//    juce::String comments;
//    MoveNode (){ parent = continuation = variation = nullptr; move = Stockfish::Move::MOVE_NONE; comments = String::empty; }
//    MoveNode (const MoveNode* other)
//    {
//        this->parent = other->parent;
//        this->continuation = other->continuation;
//        this->variation = other->variation;
//        this->move = other->move;
//        this->moveLabelText = String (other->moveLabelText);
//        this->comments = String (other->comments);
//    };
//    bool MoveNode::operator==(MoveNode &rhs)
//    {
//        if (this->continuation == rhs.continuation && this->variation == rhs.variation
//            && this->move == rhs.move && this->comments == rhs.comments && this->parent == rhs.parent)
//            return true;
//        return false;
//    }
//};
//
//struct InsertionResult
//{
//    MoveNode* continuationBrokenNode;
//    juce::Array<MoveNode*> variationBrokenNodes;
//};

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

    static juce::String getMoveUCI(Stockfish::Move m);
    void appendNodeToMainline (juce::ValueTree toAppend, bool isVariation = false);
    bool insertNodeBefore (juce::ValueTree referenceNode, juce::ValueTree toInsert);
	void doMainlineMove(Stockfish::Move m, juce::String moveSAN);
	void undoMove();
	void redoMove();
    
    juce::ValueTree getRootNode () const;
    juce::ValueTree getCurrentlyViewedNode () const;

    const Stockfish::Position& getCurrentlyViewedPosition () const;
    juce::String getMoveSAN(Stockfish::Move m);

    int getPlyCount();
    int repetitions();
    bool isDraw();
    bool isStalement();

    bool is_legal(Stockfish::Move move) const;
    Stockfish::Piece piece_on(Stockfish::Square square) const;
    Stockfish::Color side_to_move() const;
private:
    Stockfish::Position rootPosition, currentlyViewedPosition;
    juce::ValueTree viewedNode, rootNode; // this holds all the actual data
    OwnedArray<Stockfish::StateInfo> stateInfos;
};