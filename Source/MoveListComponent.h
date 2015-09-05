/*
  ==============================================================================

    MoveListRectangle.h
    Created: 13 Aug 2015 4:00:58pm
    Author:  ZA0005

  ==============================================================================
*/

#ifndef MOVELISTCOMPONENT_H_INCLUDED
#define MOVELISTCOMPONENT_H_INCLUDED

#include "../JuceLibraryCode/JuceHeader.h"

static const juce::Identifier continuation("continuation");
static const juce::Identifier variation("variation");
static const juce::Identifier move("move");
static const juce::Identifier comments("comments");
static const juce::Identifier moveLabelText("moveLabelText");

//==============================================================================
/*
*/
class MoveLabel : public Label
{
public:
    MoveLabel () {};
    MoveLabel (juce::ValueTree m) { moveNode = m; };
    void mouseDown (const MouseEvent& event) override
    {
        if (event.mods == juce::ModifierKeys::leftButtonModifier)
        {
        }
    }
private:
    juce::ValueTree moveNode;
};

class MoveListComponent    : public Component
{
public:
    MoveListComponent ()
    {
        setBounds (0, 0, 601, 435);
        horizontalPadding = verticalPadding = 7;
        nextLabelXY.setXY (horizontalPadding, verticalPadding);
    }

    // This recreates the entire movelist and makes sure the labels are inside the parent
    void updateMoveList (Game* g)
    {
        moveLabels.clear ();
        addNode(g->getRootNode().getChildWithName(continuation));
        fixLabelCoords ();
    }

    void paint (Graphics& g)
    {

        g.fillAll (Colours::aquamarine);   // clear the background

        g.setColour (Colours::black);
        g.drawRect (getLocalBounds(), 1);   // draw an outline around the component

        g.setColour (Colours::red);
        g.setFont (14.0f);
        g.drawText ("MoveListRectangle" + String(moveLabels.size()), getLocalBounds(),
                    Justification::centred, true);   // draw some placeholder text
    }

    void resized()
    {
        // This method is where you should set the bounds of any child
        // components that your component contains..
        //setBounds(0,0,getBoundsInParent().getWidth() - 8, 600);
        // just resize them all, pretty low cost
        fixLabelCoords ();
    }

    int horizontalPadding, verticalPadding;
private:

    // each item has a corresponding label
    juce::OwnedArray<MoveLabel> moveLabels;
    juce::Point<int> nextLabelXY;
    void fixLabelCoords ()
    {
        nextLabelXY.setXY (horizontalPadding, verticalPadding);
        for (int i = 0; i < moveLabels.size (); ++i)
        {
            if (nextLabelXY.getX () + moveLabels[i]->getFont ().getStringWidthFloat (moveLabels[i]->getText ()) + 3 > getWidth ())
                nextLabelXY.setXY (horizontalPadding, nextLabelXY.getY () + moveLabels[i]->getFont ().getHeight () + verticalPadding);
            moveLabels[i]->setBounds (nextLabelXY.getX (), nextLabelXY.getY (),
                moveLabels[i]->getFont ().getStringWidthFloat (moveLabels[i]->getText ()) + horizontalPadding,
                moveLabels[i]->getFont ().getHeight () + 2);
            nextLabelXY.setX (nextLabelXY.getX () + moveLabels[i]->getWidth ());
        }
    };
    void addNode(juce::ValueTree vt)
    {
        if (vt.isValid())
        {
            juce::String text = vt.getProperty(moveLabelText);
            addMoveLabel(text, false);
            addNode(vt.getChildWithName(variation));
            addNode(vt.getChildWithName(continuation));
        }
        else
        {
            int a = 3;
        }
    }
    void addMoveLabel (const juce::String &moveText, bool isVariation)
    {
        moveLabels.add (new MoveLabel ());
        moveLabels.getLast ()->setColour (juce::Label::textColourId, Colours::brown);
        moveLabels.getLast ()->setFont (18.0f);
        moveLabels.getLast ()->setText (moveText, NotificationType::dontSendNotification);
        moveLabels.getLast ()->setEditable (false);
        toFront (moveLabels.getLast ());
        moveLabels.getLast ()->addMouseListener (this, false);
        addAndMakeVisible (moveLabels.getLast ());
    }

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MoveListComponent)
};


#endif  // MOVELISTCOMPONENT_H_INCLUDED
