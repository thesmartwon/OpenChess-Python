#include "JuceHeader.h"
#include "BoardPosition/stockfish/position.h"

#pragma once

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
    Stockfish::Move move;
	Stockfish::Position* pos;
};