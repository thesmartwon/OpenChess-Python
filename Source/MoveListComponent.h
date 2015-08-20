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

//==============================================================================
/*
*/
class MoveLabel : public Label
{
public:
    MoveLabel () {};
    MoveLabel (MoveNode* m) { moveNode = m; };
    ~MoveLabel () {};
    void mouseDown (const MouseEvent& event) override
    {
        if (event.mods == juce::ModifierKeys::leftButtonModifier)
        {
        }
    }
private:
	MoveNode* moveNode;
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

    ~MoveListComponent ()
    {
    }

    void updateMoveList (Game* g)
    {
        // since a move can be inserted or deleted anywhere, it's best to recreate the movelist every time
        moveLabels.clear ();
        /*for (int i = 0; i < updatedMoveListItems.size (); ++i)
        {
            moveLabels.add (new MoveLabel (updatedMoveListItems[i]));
            
            moveLabels.getLast()->setFont (18.0f);
            moveLabels.getLast()->setText (updatedMoveListItems[i]->moveLabelText, NotificationType::dontSendNotification);
            moveLabels.getLast()->setEditable (false);
            toFront (moveLabels.getLast());
            moveLabels.getLast()->addMouseListener (this, false);
            addAndMakeVisible (moveLabels.getLast());
        }*/
        fixLabelCoords ();
    }

    void paint (Graphics& g)
    {
        /* This demo code just fills the component's background and
           draws some placeholder text to get you started.

           You should replace everything in this method with your own
           drawing code..
        */

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

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MoveListComponent)
};


#endif  // MOVELISTCOMPONENT_H_INCLUDED
