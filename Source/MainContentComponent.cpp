/*
  ==============================================================================

    This file was auto-generated!

  ==============================================================================
*/

#include "MainContentComponent.h"

//==============================================================================
MainContentComponent::MainContentComponent ()
{
    menuBarHeight = 24;
    addAndMakeVisible (menuBar = new MenuBarComponent(this));
    addAndMakeVisible (boardTabbedComponent = new BoardTabbedComponent ());
    setSize (1351, 792);

    //openGLContext.setContinuousRepainting (true);
    openGLContext.attachTo (*this);
}

MainContentComponent::~MainContentComponent ()
{
    if (openGLContext.getTargetComponent () == this)
        openGLContext.detach ();
}

void MainContentComponent::paint (Graphics& g)
{
    g.fillAll (Colour (0xff001F36));

    g.setFont (Font (16.0f));
    g.setColour (Colours::white);
    g.drawText ("Hello World!", getLocalBounds(), Justification::centred, true);
    
}

ApplicationCommandTarget* MainContentComponent::getNextCommandTarget ()
{
    // this will return the next parent component that is an ApplicationCommandTarget (in this
    // case, there probably isn't one, but it's best to use this method in your own apps).
    return findFirstTargetParentComponent ();
}


bool MainContentComponent::perform (const InvocationInfo& info)
{
    MainWindow* mainWindow = MainWindow::getMainWindow ();

    if (mainWindow == nullptr)
        return true;

    switch (info.commandID)
    {
    case MainWindow::newFile:
        break;

    case MainWindow::openFile:
        break;

    case MainWindow::recentFiles:
        break;

    case MainWindow::saveFiles:
        break;

    case MainWindow::undo:
        boardTabbedComponent->undoMove();
        break;

    case MainWindow::redo:
        boardTabbedComponent->redoMove ();
        break;

    case MainWindow::useLookAndFeelV1:
        LookAndFeel::setDefaultLookAndFeel (&lookAndFeelV1);
        break;

    case MainWindow::useLookAndFeelV2:
        LookAndFeel::setDefaultLookAndFeel (&lookAndFeelV2);
        break;

    case MainWindow::useLookAndFeelV3:
        LookAndFeel::setDefaultLookAndFeel (&lookAndFeelV3);
        break;


    default:
        return false;
    }

    return true;
}

void MainContentComponent::resized()
{
    // This is called when the MainAppWindow is resized.
    // If you add any child components, this is where you should
    // update their positions.
    setBounds (getBoundsInParent ());
	boardTabbedComponent->setBounds (0,
                                   menuBarHeight,
                                   getWidth (),
                                   getHeight () - menuBarHeight);
    menuBar->setBounds (0, 0, boardTabbedComponent->getWidth (), menuBarHeight);
}

PopupMenu MainContentComponent::getDummyPopupMenu ()
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

StringArray MainContentComponent::getMenuBarNames ()
{
    const char* const names[] = { "File", "Edit", "Tabs", "Misc", nullptr };

    return StringArray (names);
}

void MainContentComponent::getAllCommands (Array<CommandID>& commands)
{
    // this returns the set of all commands that this target can perform..
    const CommandID ids[] = { MainWindow::undo,
                              MainWindow::redo,
                              MainWindow::newFile,
                              MainWindow::openFile,
                              MainWindow::recentFiles,
                              MainWindow::saveFiles,
                              MainWindow::useLookAndFeelV1,
                              MainWindow::useLookAndFeelV2,
                              MainWindow::useLookAndFeelV3
    };

    commands.addArray (ids, numElementsInArray (ids));
}

void MainContentComponent::getCommandInfo (CommandID commandID, ApplicationCommandInfo & result)
{
    const String fileCategory ("Demos");
    const String appearanceCategory ("General");

    switch (commandID)
    {
    case MainWindow::newFile:
        result.setInfo ("New Game", "Creates a new game", fileCategory, 0);
        result.addDefaultKeypress ('n', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        break;

    case MainWindow::openFile:
        result.setInfo ("Open Game", "Open a chess game", fileCategory, 0);
        result.addDefaultKeypress ('o', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        break;

    case MainWindow::recentFiles:
        result.setInfo ("Recent files", "Recently opened chess games", fileCategory, 0);
        result.addDefaultKeypress ('p', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        break;

    case MainWindow::saveFiles:
        result.setInfo ("Save unsaved files", "New and edited files", fileCategory, 0);
        result.addDefaultKeypress ('s', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        break;

    case MainWindow::undo:
        result.setInfo ("Undo", "Undo last move or action", fileCategory, 0);
        result.addDefaultKeypress ('z', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        break;

    case MainWindow::redo:
        result.setInfo ("Redo", "Redo last undone move or action", fileCategory, 0);
        result.addDefaultKeypress ('z', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier | juce::ModifierKeys::shiftModifier);
        break;

    case MainWindow::useLookAndFeelV1:
        result.setInfo ("Use LookAndFeel_V1", String::empty, appearanceCategory, 0);
        result.addDefaultKeypress ('8', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        result.setTicked (typeid (LookAndFeel_V1) == typeid (getLookAndFeel ()));
        break;

    case MainWindow::useLookAndFeelV2:
        result.setInfo ("Use LookAndFeel_V2", String::empty, appearanceCategory, 0);
        result.addDefaultKeypress ('9', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        result.setTicked (typeid (LookAndFeel_V2) == typeid (getLookAndFeel ()));
        break;

    case MainWindow::useLookAndFeelV3:
        result.setInfo ("Use LookAndFeel_V3", String::empty, appearanceCategory, 0);
        result.addDefaultKeypress ('0', juce::ModifierKeys::commandModifier | juce::ModifierKeys::ctrlModifier);
        result.setTicked (typeid (LookAndFeel_V3) == typeid (getLookAndFeel ()));
        break;

    default:
        break;
    }
}

PopupMenu MainContentComponent::getMenuForIndex (int menuIndex, const String& /*menuName*/)
{
    ApplicationCommandManager* commandManager = &MainWindow::getApplicationCommandManager ();

    PopupMenu menu;

    if (menuIndex == 0)
    {
        menu.addCommandItem (commandManager, MainWindow::newFile);
        menu.addCommandItem (commandManager, MainWindow::openFile);
        menu.addCommandItem (commandManager, MainWindow::recentFiles);
        menu.addCommandItem (commandManager, MainWindow::saveFiles);
        menu.addSeparator ();
        menu.addCommandItem (commandManager, StandardApplicationCommandIDs::quit, "Quit");
    } else if (menuIndex == 1)
    {
        menu.addCommandItem (commandManager, MainWindow::undo);
        menu.addCommandItem (commandManager, MainWindow::redo);
        menu.addSeparator ();
    } else if (menuIndex == 2)
	{
        menu.addCommandItem (commandManager, MainWindow::useLookAndFeelV1);
        menu.addCommandItem (commandManager, MainWindow::useLookAndFeelV2);
        menu.addCommandItem (commandManager, MainWindow::useLookAndFeelV3);
        menu.addSeparator ();
		menu.addItem(3000, "Tabs at Top", true, false);
		menu.addItem(3001, "Tabs at Bottom", true, false);
		menu.addItem(3002, "Tabs at Left", true, false);
		menu.addItem(3003, "Tabs at Right", true, false);
		menu.addSeparator();
	} else if (menuIndex == 3)
    {
        return getDummyPopupMenu ();
    }

    return menu;
}

void MainContentComponent::menuItemSelected (int menuItemID, int)
{
    if (menuItemID >= 3000 && menuItemID <= 3003)
    {
        if (boardTabbedComponent != nullptr)
        {
            TabbedButtonBar::Orientation o = TabbedButtonBar::TabsAtTop;

            if (menuItemID == 3001) o = TabbedButtonBar::TabsAtBottom;
            if (menuItemID == 3002) o = TabbedButtonBar::TabsAtLeft;
            if (menuItemID == 3003) o = TabbedButtonBar::TabsAtRight;

			//boardTabbedComponent->setOrientation(o);
        }
    }
}

