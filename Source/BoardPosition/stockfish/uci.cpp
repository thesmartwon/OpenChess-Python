/*
  Stockfish, a UCI chess playing engine derived from Glaurung 2.1
  Copyright (C) 2004-2008 Tord Romstad (Glaurung author)
  Copyright (C) 2008-2015 Marco Costalba, Joona Kiiski, Tord Romstad

  Stockfish is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Stockfish is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <iostream>
#include <sstream>
#include <string>

#include "movegen.h"
#include "position.h"
#include "uci.h"

using namespace std;
using namespace Stockfish;

namespace {

  // FEN string of the initial position, normal chess
  const char* StartFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

  // Stack to keep track of the position states along the setup moves (from the
  // start position to the position just before the search starts). Needed by
  // 'draw by repetition' detection.
  Stockfish::UCI::StateStackPtr SetupStates;
  

  // position() is called when engine receives the "position" UCI command.
  // The function sets up the position described in the given FEN string ("fen")
  // or the starting position ("startpos") and then makes the moves given in the
  // following move list ("moves").

  

} // namespace

namespace MoveGen
{
    template<PieceType Pt, bool Checks> FORCE_INLINE
        ExtMove* generate_moves (const Position& pos, ExtMove* moveList, Color us, const CheckInfo* ci)
    {

        assert (Pt != KING && Pt != PAWN);

        const Square* pl = pos.list<Pt> (us);

        for (Square from = *pl; from != SQ_NONE; from = *++pl)
        {
            if (Checks)
            {
                if ((Pt == BISHOP || Pt == ROOK || Pt == QUEEN)
                    && !(PseudoAttacks[Pt][from] & ci->checkSq[Pt]))
                    continue;

                if (ci->dcCandidates && (ci->dcCandidates & from))
                    continue;
            }

            Bitboard b = pos.attacks_from<Pt> (from);

            if (Checks)
                b &= ci->checkSq[Pt];

            while (b)
                (moveList++)->move = make_move (from, pop_lsb (&b));
        }

        return moveList;
    }
} //namespace MoveGen



/// UCI::square() converts a Square to a string in algebraic notation (g1, a7, etc.)

std::string UCI::square(Square s) {

  char sq[] = { char('a' + file_of(s)), char('1' + rank_of(s)), 0 }; // NULL terminated
  return sq;
}


/// UCI::move() converts a Move to a string in coordinate notation (g1f3, a7a8q).
/// The only special case is castling, where we print in the e1g1 notation in
/// normal chess mode, and in e1h1 notation in chess960 mode. Internally all
/// castling moves are always encoded as 'king captures rook'.

string UCI::move(Move m, bool chess960) {

  Square from = from_sq(m);
  Square to = to_sq(m);

  if (m == MOVE_NONE)
      return "(none)";

  if (m == MOVE_NULL)
      return "0000";

  if (type_of(m) == CASTLING && !chess960)
      to = make_square(to > from ? FILE_G : FILE_C, rank_of(from));

  string move = UCI::square(from) + UCI::square(to);

  if (type_of(m) == PROMOTION)
      move += " pnbrqk"[promotion_type(m)];

  return move;
}

bool containsTwo (ExtMove moveList[250], Move m)
{
    bool foundOne = false;
    Move recordedMove = Stockfish::Move::MOVE_NONE;
	for (int i = 0; i < 250; ++i)
    {
		if (moveList[i].move == MOVE_NONE)
			break;
        else if (to_sq(moveList[i].move) == to_sq(m))
        {
            if (!foundOne)
            {
                foundOne = true;
                recordedMove = moveList[i].move;
            }
            else if (recordedMove != moveList[i].move)
            {
                return true;
            }
        }
    }
    return false;
}

bool hasLegalMoves (ExtMove moveList[250], Position p)
{
    for (int i = 0; i < 250; ++i)
    {
        if (moveList[i].move == Stockfish::Move::MOVE_NONE)
            return false;
        if (p.pseudo_legal (moveList[i].move) && p.legal (moveList[i].move, p.pinned_pieces(p.side_to_move())))
            return true;
    }
}

string UCI::movePGN (Move m, Position& p, bool chess960)
{
    if (m == MOVE_NONE)
        return "(none)";

    if (m == MOVE_NULL)
        return "0000";
    string moveTextBefore = move (m, chess960);
    string moveTextAfter = "";

    if (type_of (m) == CASTLING && !chess960)
    {
        if (moveTextBefore == "e1h1" || moveTextBefore == "e8h8")
            moveTextAfter += "O-O";
        else
            moveTextAfter += "O-O-O";
    }
    else if (type_of (m) == PROMOTION)
    {
        Stockfish::StateInfo* lastState = p.st;
        p.undo_move (m);
        // is it a capture?
        if (p.piece_on (to_sq (m)) != Stockfish::Piece::NO_PIECE)
            moveTextAfter = moveTextBefore[0] + "x";
        p.do_move (m, *lastState);

        // dxc8=Q
        moveTextAfter += moveTextBefore.substr (2, 4) + "=" + (char)(toupper(moveTextBefore[5]));
    }
    else //normal move
    {
        if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::BISHOP)
        {
            moveTextAfter = "B";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            Stockfish::StateInfo* lastState = p.st;
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NONE };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<BISHOP, false> (tmpPos, moveListPtr, p.side_to_move (), chkInfo);
            if (containsTwo (moveList, m))
                moveTextAfter += moveTextBefore.substr (0, 2);
            p.do_move (m, *lastState);
            moveTextAfter += moveTextBefore.substr (2, 4);
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::KNIGHT)
        {
            moveTextAfter = "N";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            Stockfish::StateInfo* lastState = p.st;
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NONE };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<KNIGHT, false> (tmpPos, moveListPtr, p.side_to_move (), chkInfo);
            if (containsTwo (moveList, m))
                moveTextAfter += moveTextBefore.substr (0, 1);
            p.do_move (m, *lastState);
			moveTextAfter += moveTextBefore.substr(2, 4);
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::ROOK)
        {
            moveTextAfter = "R";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            Stockfish::StateInfo* lastState = p.st;
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NONE };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<ROOK, false> (tmpPos, moveListPtr, p.side_to_move (), chkInfo);
            if (containsTwo (moveList, m))
                moveTextAfter += moveTextBefore.substr (0, 1);
            p.do_move (m, *lastState);
            moveTextAfter += moveTextBefore.substr (2, 4);
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::QUEEN)
        {
            moveTextAfter = "Q";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            Stockfish::StateInfo* lastState = p.st;
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NONE };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<QUEEN, false> (tmpPos, moveListPtr, p.side_to_move (), chkInfo);
            if (containsTwo (moveList, m))
                moveTextAfter += moveTextBefore.substr (0, 1);
            p.do_move (m, *lastState);
            moveTextAfter += moveTextBefore.substr (2, 4);
        }
        else //pawn
        {
			Stockfish::StateInfo* lastState = p.st;
            p.undo_move (m);
            // is it a capture?
            if (p.piece_on (to_sq (m)) != Stockfish::Piece::NO_PIECE)
                moveTextAfter = moveTextBefore.substr (0,1) + "x" + moveTextBefore.substr (2, 4);
            else
                moveTextAfter = moveTextBefore.substr (2, 4);
            p.do_move (m, *lastState);
        }
        //check and checkmate
        if (p.checkers () != 0) //check
        {
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NONE };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            // TODO: figure out why this sometimes generates illegal moves
            moveListPtr = Stockfish::generate<Stockfish::GenType::LEGAL> (tmpPos, moveListPtr);
            if (!hasLegalMoves(moveList, tmpPos))//checkmate?
                moveTextAfter += "#";
            else
                moveTextAfter += "+";
        }
    }
    return moveTextAfter;
}

/// UCI::to_move() converts a string representing a move in coordinate notation
/// (g1f3, a7a8q) to the corresponding legal Move, if any.

Move UCI::to_move(const Position& pos, string& str) {

  if (str.length() == 5) // Junior could send promotion piece in uppercase
      str[4] = char(tolower(str[4]));

  for (MoveList<LEGAL> it(pos); *it; ++it)
      if (str == UCI::move(*it, pos.is_chess960()))
          return *it;

  return MOVE_NONE;
}
