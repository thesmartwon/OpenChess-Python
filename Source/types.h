#include "JuceHeader.h"
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

struct MoveListItem
{
    MoveListItem () { moveNode = {}; lblMove = nullptr; }
    MoveListItem (MoveNode moveNode, Label* lblMove) { this->moveNode = moveNode; this->lblMove = lblMove; }
    ScopedPointer<Label> lblMove;
    MoveNode moveNode;
};