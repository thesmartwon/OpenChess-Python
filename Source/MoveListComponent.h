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
class MoveListComponent    : public Component
{
public:
    MoveListComponent ()
    {
        setBounds (0, 0, 601, 435);
        horizontalPadding = verticalPadding = 7;
        nextLabelXY.setXY (horizontalPadding, verticalPadding);
    }
    MoveListComponent (const juce::OwnedArray<MoveListItem>& updatedMoveListItems)
    {
        // In your constructor, you should add any child components, and
        // initialise any special settings that your component needs.
        setBounds (0, 0, 601, 435);
        horizontalPadding = verticalPadding = 5;
        nextLabelXY.setXY (horizontalPadding, verticalPadding);
        for (int i = 0; i < updatedMoveListItems.size (); ++i)
            moveListItems.add (updatedMoveListItems[i]);
    }

    ~MoveListComponent ()
    {
    }

    void updateMoveList (const juce::OwnedArray<MoveListItem>& updatedMoveListItems)
    {
        // since a move can be inserted or deleted anywhere, it's best to recreate the movelist every time
        // where it is different than the last move list
        moveListItems.resize (updatedMoveListItems.size());
        const int numToAdd = updatedMoveListItems.size() - moveLabels.size();
        if (numToAdd > 0)
            for (int i = 0; i < numToAdd; ++i)
                moveLabels.add (new Label ());
        else if (numToAdd < 0)
        {
            nextLabelXY.setXY (moveLabels.getLast ()->getBounds ().getX (), moveLabels.getLast ()->getBounds ().getY ());
            moveLabels.removeRange (updatedMoveListItems.size (), -numToAdd);
        }
        for (int i = 0; i < updatedMoveListItems.size (); ++i)
        {
            jassert (updatedMoveListItems[i] != nullptr);
            if (! (moveListItems[i] == updatedMoveListItems[i]))
            { // a difference!
                Label* newLabel = moveLabels[i];
                newLabel->setFont (18.0f);
                newLabel->setText (updatedMoveListItems[i]->moveLabelText, NotificationType::dontSendNotification);
                if (nextLabelXY.getX() + newLabel->getFont().getStringWidthFloat (newLabel->getText()) + 3 > getWidth())
                    nextLabelXY.setXY (horizontalPadding, nextLabelXY.getY() + newLabel->getFont().getHeight() + verticalPadding);
                newLabel->setEditable (false);
                newLabel->setBounds (nextLabelXY.getX(), nextLabelXY.getY (),
                                     newLabel->getFont().getStringWidthFloat (newLabel->getText()) + horizontalPadding,
                                     newLabel->getFont().getHeight () + 2);
                this->toFront (newLabel);
                newLabel->addMouseListener (this, false);
                addAndMakeVisible (newLabel);
                nextLabelXY.setX (nextLabelXY.getX() + newLabel->getWidth());
            }
        }

        moveListItems.clear ();
        for (int i = 0; i < updatedMoveListItems.size (); ++i)
            if (!(moveListItems[i] == updatedMoveListItems[i]))
                this->moveListItems.add (updatedMoveListItems[i]);
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
        //setBounds(0,0,getBoundsInParent().getWidth() - 8,600);
        /*for (int i = 0; i < moveLabels.size (); ++i)
        {
            if (moveLabels[i]->getX () + moveLabels[i]->getWidth () > getWidth ())
            {
                for (int j = i; j < moveLabels.size () - i; ++j)
                {
                    if (nextLabelXY.getX () + moveLabels[j]->getFont ().getStringWidthFloat (moveLabels[j]->getText ()) + 3 > getWidth ())
                        nextLabelXY.setXY (horizontalPadding, nextLabelXY.getY () + moveLabels[j]->getFont ().getHeight () + verticalPadding);
                    moveLabels[j]->setBounds (nextLabelXY.getX (), nextLabelXY.getY (),
                        moveLabels[j]->getFont ().getStringWidthFloat (moveLabels[j]->getText ()) + horizontalPadding,
                        moveLabels[j]->getFont ().getHeight () + 2);
                    nextLabelXY.setX (nextLabelXY.getX () + moveLabels[j]->getWidth ());
                }
                break;
            }
        }*/
    }

    int horizontalPadding, verticalPadding;
private:
    juce::Array<MoveListItem*> moveListItems;
    // each label has a corresponding item
    juce::OwnedArray<Label> moveLabels;
    juce::Point<int> nextLabelXY;
    void addLabel ()
    {

    }

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MoveListComponent)
};


#endif  // MOVELISTCOMPONENT_H_INCLUDED
