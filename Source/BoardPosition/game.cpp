#include "stdafx.h" //if this doesnt compile, change it to #include "../stdafx/h". very annoying
#include "game.h"

Game::Game ()
{
    rootPosition.set ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);
	currentlyViewedPosition.set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);
    rootNode = currentlyViewedNode = nullptr;
}

Game::Game (const juce::String startingFEN)
{
    rootPosition.set (startingFEN.toStdString(), false);
	currentlyViewedPosition.set(startingFEN.toStdString(), false);

    rootNode = currentlyViewedNode = nullptr;
}

Stockfish::Position Game::getCurrentlyViewedPosition () const
{
	return currentlyViewedPosition;
}

void Game::appendNode(MoveNode* referenceMove, MoveNode* toAppend, bool isVariation)
{
    if (isVariation)
    {
        jassert (referenceMove->variation != nullptr);
        referenceMove->variation = toAppend;
    }
    else
    {
        jassert (referenceMove->continuation != nullptr);
        referenceMove->continuation = toAppend;
    }
    currentlyViewedNode = referenceMove;
}

void Game::appendNodeToMainline (MoveNode* toAppend, bool isVariation)
{
    if (rootNode == nullptr)
    {
        rootNode = currentlyViewedNode = toAppend;
        return;
    }
    MoveNode* curNode = rootNode;
    while (curNode->continuation != nullptr)
            curNode = curNode->continuation;

    if (isVariation)
    {
        jassert (curNode->variation == nullptr);
        curNode->variation = toAppend;
    }
    else
    {
        jassert (curNode->continuation == nullptr);
        curNode->continuation = toAppend;
    }
    currentlyViewedNode = toAppend;
}

bool Game::insertNodeBefore (MoveNode* referenceNode, MoveNode* toInsert)
{
    InsertionResult result = {};
    Stockfish::Position tmpPos = currentlyViewedPosition;
    MoveNode* curNode = referenceNode;
    // test if move can be inserted legally
    tmpPos.do_move (toInsert->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    // the move may make any number of variations invalid or it's continuation invalid
    // test continuation validity
    while (curNode->continuation != nullptr)
    {
        if (tmpPos.pseudo_legal (curNode->move) && tmpPos.legal (curNode->move, tmpPos.pinned_pieces (tmpPos.side_to_move())))
        {
            tmpPos.do_move (curNode->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
            curNode = curNode->continuation;
        }
        else
        {
            result.continuationBrokenNode = curNode;
            return false;
        }
    }
    currentlyViewedNode = toInsert;
    return true;
}

void Game::doMainlineMove(Stockfish::Move m, juce::String moveSAN)
{
    // create the new node to put in the binary tree
	MoveNode* newNode = new MoveNode();
	newNode->parent = currentlyViewedNode;
	newNode->continuation = nullptr;
	newNode->variation = nullptr;
	newNode->move = m;
	newNode->comments = String::empty;
	String labelText;
	if (currentlyViewedPosition.game_ply() % 2 == 1)
		labelText = std::to_string(currentlyViewedPosition.game_ply() - currentlyViewedPosition.game_ply() / 2) + ". " + moveSAN, NotificationType::dontSendNotification;
	else
		labelText = moveSAN + " ";
	newNode->moveLabelText = labelText;

    redoStack.clear();
	currentlyViewedPosition.do_move(newNode->move, *(Stockfish::StateInfo *)calloc(1, sizeof(Stockfish::StateInfo)));
	appendNodeToMainline(newNode);
}

void Game::undoMove()
{
	currentlyViewedPosition.undo_move(currentlyViewedNode->move);
	redoStack.add(currentlyViewedNode);
	currentlyViewedNode = currentlyViewedNode->parent;
}

void Game::redoMove()
{
	if (redoStack.size() > 0)
	{
		currentlyViewedPosition.do_move(redoStack.getLast()->move, *(Stockfish::StateInfo *)calloc(1, sizeof(Stockfish::StateInfo)));
		currentlyViewedNode = redoStack.remove(redoStack.size() - 1);
	}
}

void Game::setCurrentlyViewedNode (MoveNode* nodeToView)
{
    currentlyViewedNode = nodeToView;
}

MoveNode* Game::getCurrentlyViewedNode () const
{
    return currentlyViewedNode;
}
