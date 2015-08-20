#include "stdafx.h" //if this doesnt compile, change it to #include "../stdafx/h". very annoying
#include "game.h"

Game::Game ()
{
    rootPosition.set ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);
    rootNode = nullptr;
}

Game::Game (const juce::String startingFEN)
{
    rootPosition.set (startingFEN.toStdString(), false);
    rootNode = nullptr;
}

Stockfish::Position Game::positionAtNode (MoveNode* referenceNode) const
{
    Stockfish::Position tmpPos = Stockfish::Position(rootPosition);
    std::stack<MoveNode*> path;
    if (rootNode == nullptr || rootNode == referenceNode)
    {
        return rootPosition;
    }
    path.push(rootNode);
    while (path.empty () == false && path.top () != referenceNode)
    {
        // Pop the top item from stack
        MoveNode *node = path.top ();
        path.pop ();

        // Push right and left children of the popped node to stack
        if (node->variation)
            path.push (node->variation);
        if (node->continuation)
            path.push (node->continuation);
    }
    std::stack<MoveNode*> reversedPath;
    while (path.empty() == false)
    {
        MoveNode *node = path.top ();
        path.pop ();
        reversedPath.push (node);
    }
    tmpPos.do_move (rootNode->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    while (reversedPath.empty () == false)
    {
        MoveNode *node = reversedPath.top ();
        reversedPath.pop ();
        tmpPos.do_move (node->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    }

    return tmpPos;
}

Stockfish::Position Game::getCurrentlyViewedPosition () const
{
    if (currentlyViewedNode != nullptr)
        return positionAtNode(currentlyViewedNode);
    else return rootPosition;
}

void Game::appendMove (MoveNode* referenceMove, MoveNode* toAppend, bool isVariation)
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

void Game::appendMoveToMainline (MoveNode* toAppend, bool isVariation)
{
    if (rootNode == nullptr)
    {
        rootNode = toAppend;
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

bool Game::insertMoveBefore (MoveNode* referenceNode, MoveNode* toInsert)
{
    InsertionResult result = {};
    Stockfish::Position tmpPos = positionAtNode(referenceNode);
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

bool Game::hasRootNode () const
{
    if (rootNode == nullptr)
        return false;
    else return true;
}

void Game::setCurrentlyViewedNode (MoveNode* nodeToView)
{
    currentlyViewedNode = nodeToView;
}

MoveNode* Game::getCurrentlyViewedNode () const
{
    return currentlyViewedNode;
}
