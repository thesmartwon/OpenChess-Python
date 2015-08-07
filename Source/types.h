#include "JuceHeader.h"
#include "BoardPosition/stockfish/position.h"

#pragma once

enum MessageType
{
    MSG_GENERIC_MESSAGE,
    MSG_BOARD_STATE
};

class GenericMessage : public Message
{
public:
    GenericMessage (MessageType msType) : messageType (msType) {};
    MessageType messageType;
};

class MoveListMessage : public GenericMessage
{
public:
    MoveListMessage () : GenericMessage (MSG_BOARD_STATE){};
    juce::Array<Stockfish::Move> moveList;
};