#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardPosition/stockfish/position.h"

#pragma once

struct MoveNode
{
    MoveNode* parent;
    MoveNode* continuation;
    MoveNode* variation;
    Stockfish::Move move;
	juce::String moveLabelText;
    juce::String comments;
    MoveNode () { parent = continuation = variation = nullptr; move = Stockfish::Move::MOVE_NONE; comments = String::empty; }
    MoveNode (const MoveNode* other)
    {
        this->parent = other->parent;
        this->continuation = other->continuation;
        this->variation = other->variation;
        this->move = other->move;
        this->comments = String(other->comments);
    };
    MoveNode (MoveNode* parent, MoveNode* continuation, MoveNode* variation, Stockfish::Move move, juce::String comments)
    {
        this->parent = parent;
        this->continuation = continuation;
        this->variation = variation;
        this->move = move;
        this->comments = String(comments);
    }
    bool MoveNode::operator==(MoveNode &rhs)
    {
        if (this->continuation == rhs.continuation && this->variation == rhs.variation
            && this->move == rhs.move && this->comments == rhs.comments && this->parent == rhs.parent)
            return true;
        return false;
    }
};

enum PieceColor
{
    white = 0,
    black = 1,
    noColor = 2
};

enum MessageType
{
    MSG_GENERIC_MESSAGE,
    MSG_MOVEMESSAGE
};

class GenericMessage : public Message
{
public:
    GenericMessage (MessageType msType) : messageType (msType) {};
    MessageType messageType;
};

class MoveMessage : public GenericMessage
{
public:
    MoveMessage () : GenericMessage (MSG_MOVEMESSAGE){};
    juce::String moveSAN;
    juce::String moveUCI;
    Stockfish::Move move;
};