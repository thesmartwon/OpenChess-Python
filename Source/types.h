#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardPosition/stockfish/position.h"

#pragma once

struct MoveNode
{
    MoveNode* continuation;
    MoveNode* variation;
    Stockfish::Move move;
    juce::String comments;
    MoveNode () {}
    MoveNode (MoveNode* continuation, MoveNode* variation, Stockfish::Move move, juce::String comments)
    {
        this->continuation = continuation;
        this->variation = variation;
        this->move = move;
        this->comments = comments;
    }
    bool MoveNode::operator==(MoveNode &rhs)
    {
        if (this->continuation == rhs.continuation && this->variation == rhs.variation
            && this->move == rhs.move && this->comments == rhs.comments)
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

// contains a node in the movelist tree and the text of the move
struct MoveListItem
{
    MoveListItem () { moveNode = {}; moveLabelText = String::empty; }
    MoveListItem (const MoveListItem& m) { this->moveNode = m.moveNode; this->moveLabelText = m.moveLabelText; }
    MoveListItem (MoveNode moveNode, String moveText) { this->moveNode = moveNode; this->moveLabelText = moveText; }
    String moveLabelText;
    MoveNode moveNode;
    bool MoveListItem::operator==(MoveListItem &rhs)
    {
        if (this->moveNode == rhs.moveNode && this->moveLabelText == rhs.moveLabelText)
            return true;
        return false;
    }
};