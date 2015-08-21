#include "../JuceLibraryCode/JuceHeader.h"
#include "BoardPosition/stockfish/position.h"

#pragma once

enum MessageType
{
    MSG_GENERIC_MESSAGE,
    MSG_MOVEMESSAGE
};

struct GenericMessage : public Message
{
    GenericMessage (MessageType msType) : messageType (msType) {};
    MessageType messageType;
};

struct MoveMessage : public GenericMessage
{
    MoveMessage () : GenericMessage (MSG_MOVEMESSAGE){};
    juce::String moveSAN;
    juce::String moveUCI;
    Stockfish::Move move;
};