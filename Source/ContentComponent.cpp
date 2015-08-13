/*
  ==============================================================================

    This file was auto-generated!

  ==============================================================================
*/

#include "ContentComponent.h"

//==============================================================================
ContentComponent::ContentComponent ()
{
    addAndMakeVisible (menuBar = new MenuBarComponent(this));
    menuBar->setBounds (0, 0, 886, 24);
    addAndMakeVisible (boardTabsComponent = new BoardTabsComponent ());
    boardTabsComponent->setBounds (0,
                                  24,
                                  boardTabsComponent->getWidth (),
                                  boardTabsComponent->getHeight ());
    setSize (886, 790);


}

ContentComponent::~ContentComponent ()
{
    //this is a test hello therr yayyyy
}

void ContentComponent::paint (Graphics& g)
{
    g.fillAll (Colour (0xff001F36));

    g.setFont (Font (16.0f));
    g.setColour (Colours::white);
    g.drawText ("Hello World!", getLocalBounds(), Justification::centred, true);
    
}

ApplicationCommandTarget* ContentComponent::getNextCommandTarget ()
{
    // this will return the next parent component that is an ApplicationCommandTarget (in this
    // case, there probably isn't one, but it's best to use this method in your own apps).
    return findFirstTargetParentComponent ();
}


bool ContentComponent::perform (const InvocationInfo& info)
{
    return false;
}

void ContentComponent::resized()
{
    // This is called when the MainAppWindow is resized.
    // If you add any child components, this is where you should
    // update their positions.
    setBounds (getBoundsInParent ());
    boardTabsComponent->setBounds (0,
                                   24,
                                   boardTabsComponent->getWidth (),
                                   boardTabsComponent->getHeight ());
}

PopupMenu ContentComponent::getDummyPopupMenu ()
{
    PopupMenu m;
    m.addItem (1, "Normal item");
    m.addItem (2, "Disabled item", false);
    m.addItem (3, "Ticked item", true, true);
    m.addColouredItem (4, "Coloured item", Colours::green);
    m.addSeparator ();
    m.addSeparator ();

    for (int i = 0; i < 8; ++i)
    {
        PopupMenu subMenu;

        for (int s = 0; s < 8; ++s)
        {
            PopupMenu subSubMenu;

            for (int item = 0; item < 8; ++item)
                subSubMenu.addItem (1000 + (i * s * item), "Item " + String (item + 1));

            subMenu.addSubMenu ("Sub-sub menu " + String (s + 1), subSubMenu);
        }

        m.addSubMenu ("Sub menu " + String (i + 1), subMenu);
    }

    return m;
}

StringArray ContentComponent::getMenuBarNames ()
{
    const char* const names[] = { "Demo", "Look-and-feel", "Tabs", "Misc", nullptr };

    return StringArray (names);
}

PopupMenu ContentComponent::getMenuForIndex (int menuIndex, const String& /*menuName*/)
{
    ApplicationCommandManager* commandManager = &MainWindow::getApplicationCommandManager ();

    PopupMenu menu;

    if (menuIndex == 0)
    {
        menu.addItem (3000, "Tabs at Top", true, false);
        menu.addSeparator ();
        menu.addCommandItem (commandManager, StandardApplicationCommandIDs::quit, "Quit");
    } else if (menuIndex == 1)
    {
        menu.addSeparator ();
    }  else if (menuIndex == 3)
    {
        return getDummyPopupMenu ();
    }

    return menu;
}

void ContentComponent::menuItemSelected (int menuItemID, int)
{
    if (menuItemID >= 3000 && menuItemID <= 3003)
    {
        if (TabbedComponent* tabs = findParentComponentOfClass<TabbedComponent> ())
        {
            TabbedButtonBar::Orientation o = TabbedButtonBar::TabsAtTop;

            if (menuItemID == 3001) o = TabbedButtonBar::TabsAtBottom;
            if (menuItemID == 3002) o = TabbedButtonBar::TabsAtLeft;
            if (menuItemID == 3003) o = TabbedButtonBar::TabsAtRight;

            tabs->setOrientation (o);
        }
    }
}
