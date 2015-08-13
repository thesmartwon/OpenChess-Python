#pragma once

#include "JuceHeader.h"

class MoveListComponent : public juce::Viewport
{
public:
    MoveListComponent ();
    ~MoveListComponent ();

    void visibleAreaChanged (const juce::Rectangle<int>& newVisibleArea) override;
};

