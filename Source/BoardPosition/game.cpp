#include "stdafx.h" //if this doesnt compile, change it to #include "../stdafx/h". very annoying
#include "game.h"
#include "stockfish/uci.h"


static const juce::Identifier continuation("continuation");
static const juce::Identifier variation("variation");
static const juce::Identifier move("move");
static const juce::Identifier comments("comments");
static const juce::Identifier moveLabelText("moveLabelText");

Game::Game() : 
    rootNode("rootNode"),
    viewedNode("viewedNode")
{
    rootPosition.set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);
    currentlyViewedPosition.set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", false);

    viewedNode = rootNode;
}

Game::Game (const juce::String startingFEN) : 
    rootNode("rootNode"),
    viewedNode("viewedNode")
{
    rootPosition.set (startingFEN.toStdString(), false);
	currentlyViewedPosition.set(startingFEN.toStdString(), false);

    viewedNode = rootNode;
}

const Stockfish::Position& Game::getCurrentlyViewedPosition() const
{
    return currentlyViewedPosition;
}

juce::String Game::getMoveSAN(Stockfish::Move m)
{
    return juce::String(Stockfish::UCI::move_to_san(currentlyViewedPosition, m));
}

int Game::getPlyCount()
{
    return currentlyViewedPosition.game_ply();
}

int Game::repetitions()
{
    int count = 1;
    // repetitions happen in pairs
    if (currentlyViewedPosition.game_ply() > 4)
    {
        juce::ValueTree tempTree = viewedNode;
        juce::String m = tempTree.getProperty(move);
        Stockfish::Move move2 = Stockfish::Move (m.getIntValue());
        m = tempTree.getParent().getProperty(move);
        Stockfish::Move move1 = Stockfish::Move (m.getIntValue());
        tempTree = tempTree.getParent().getParent();

        bool whichMove = false;
        while (tempTree.getParent() != rootNode)
        {
            if (whichMove)
            {
                juce::String m = tempTree.getProperty(move);
                if (Stockfish::Move(m.getIntValue()) != move2)
                    break;
            }
            else
            {
                juce::String m = tempTree.getProperty(move);
                if (Stockfish::Move(m.getIntValue()) != move1)
                    break;
                count++;
            }
                
            tempTree = tempTree.getParent();
            whichMove = !whichMove;
        }
    }
    

    return count;
}

bool Game::isDraw()
{
    return currentlyViewedPosition.is_draw();
}

bool Game::isStalement()
{
    Stockfish::ExtMove moves[300] = { Stockfish::Move::MOVE_NONE };
    Stockfish::generate<Stockfish::GenType::LEGAL>(currentlyViewedPosition, moves);
    if (moves[0].move == Stockfish::Move::MOVE_NONE)
        return true;
    return false;
}

bool Game::is_legal(Stockfish::Move move) const
{
    if (currentlyViewedPosition.pseudo_legal (move) &&
        currentlyViewedPosition.legal (move, currentlyViewedPosition.pinned_pieces (currentlyViewedPosition.side_to_move ())))
        return true;
    return false;
}

Stockfish::Piece Game::piece_on(Stockfish::Square square) const
{
    return currentlyViewedPosition.piece_on(square);
}

Stockfish::Color Game::side_to_move() const
{
    return currentlyViewedPosition.side_to_move();
}

juce::String Game::getMoveUCI(Stockfish::Move m)
{
    return juce::String(Stockfish::UCI::move(m, false));
}

void Game::appendNodeToMainline (juce::ValueTree toAppend, bool isVariation)
{
    if (!rootNode.isValid())
    {
        // can't have variation of first move...
        rootNode.addChild (toAppend, -1, nullptr);
        return;
    }

    if (isVariation)
    {
        viewedNode.addChild (toAppend, -1, nullptr);
        viewedNode = toAppend;
    }
    else
    {
        viewedNode.addChild (toAppend, -1, nullptr);
        viewedNode = toAppend;
    }

    //DBG(rootNode.toXmlString());
}

bool Game::insertNodeBefore (juce::ValueTree referenceNode, juce::ValueTree toInsert)
{
    //InsertionResult result = {};
    //Stockfish::Position tmpPos = currentlyViewedPosition;
    //MoveNode* curNode = referenceNode;
    //// test if move can be inserted legally
    //tmpPos.do_move (toInsert->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    //// the move may make any number of variations invalid or it's continuation invalid
    //// test continuation validity
    //while (curNode->continuation != nullptr)
    //{
    //    if (tmpPos.pseudo_legal (curNode->move) && tmpPos.legal (curNode->move, tmpPos.pinned_pieces (tmpPos.side_to_move())))
    //    {
    //        tmpPos.do_move (curNode->move, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
    //        curNode = curNode->continuation;
    //    }
    //    else
    //    {
    //        result.continuationBrokenNode = curNode;
    //        return false;
    //    }
    //}
    //currentlyViewedNode = toInsert;
    return true;
}

void Game::doMainlineMove(Stockfish::Move m, juce::String moveSAN)
{
    // create the new node to put in the binary tree
    juce::ValueTree newNode(continuation);
    newNode.setProperty(comments, String::empty, nullptr);
    newNode.setProperty(move, m, nullptr);
	String labelText;
	if (currentlyViewedPosition.game_ply() % 2 == 0)
		labelText = std::to_string(currentlyViewedPosition.game_ply() - currentlyViewedPosition.game_ply() / 2 + 1) + ". " + moveSAN, NotificationType::dontSendNotification;
	else
		labelText = moveSAN + " ";
    newNode.setProperty(moveLabelText, labelText, nullptr);

    Stockfish::StateInfo st = {0};
    Stockfish::CheckInfo ci(currentlyViewedPosition);

    stateInfos.add (new Stockfish::StateInfo());
	currentlyViewedPosition.do_move(m, *(stateInfos.getLast()), ci, currentlyViewedPosition.gives_check(m, ci));
	appendNodeToMainline(newNode);
}

void Game::undoMove()
{
}

void Game::redoMove()
{
}

juce::ValueTree Game::getRootNode () const
{
    return rootNode;
}

juce::ValueTree Game::getCurrentlyViewedNode () const
{
    return viewedNode;
}
