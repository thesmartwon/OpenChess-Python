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
        // In your constructor, you should add any child components, and
        // initialise any special settings that your component needs.
        setBounds (0, 0, 601, 435);
    }

    ~MoveListComponent ()
    {
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

        g.setColour (Colours::white);
        g.setFont (14.0f);
        g.drawText ("MoveListRectangle", getLocalBounds(),
                    Justification::centred, true);   // draw some placeholder text
    }

    void resized()
    {
        // This method is where you should set the bounds of any child
        // components that your component contains..
        //scrollbasrwidth is 16
        //setBounds(0,0,getBoundsInParent().getWidth() - 8,600);
    }

private:
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MoveListComponent)
};


#endif  // MOVELISTCOMPONENT_H_INCLUDED
