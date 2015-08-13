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

Move containsTwo (ExtMove moveList[250], Move m)
{
    Move recordedMove = Move::MOVE_NONE;
	for (int i = 0; i < 250; ++i)
    {
		if (moveList[i].move == MOVE_NONE)
			break;
        else if (to_sq(moveList[i].move) == to_sq(m) && from_sq(moveList[i].move) != from_sq (m))
            return moveList[i].move;
    }
    return Move::MOVE_NONE;
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



static const char* PieceToChar[COLOR_NB] = { " PNBRQK", " pnbrqk" };

inline char to_char (File f, bool tolower = true)
{
    return char (f - FILE_A + (tolower ? 'a' : 'A'));
}

inline char to_char (Rank r)
{
    return char (r - RANK_1 + '1');
}

/// makes the PGN version of a move.
const std::string UCI::move_to_san (Position& pos, Move m)
{

    if (m == MOVE_NONE)
        return "(none)";

    if (m == MOVE_NULL)
        return "(null)";

    assert (MoveList<LEGAL> (pos).contains (m));

    Bitboard others, b;
    string san;
    Color us = pos.side_to_move ();
    Square from = from_sq (m);
    Square to = to_sq (m);
    Piece pc = pos.piece_on (from);
    PieceType pt = type_of (pc);

    if (type_of (m) == CASTLING)
        san = to > from ? "O-O" : "O-O-O";
    else
    {
        if (pt != PAWN)
        {
            san = PieceToChar[WHITE][pt]; // Upper case

                                          // A disambiguation occurs if we have more then one piece of type 'pt'
                                          // that can reach 'to' with a legal move.
            others = b = (pos.attacks_from (pc, to) & pos.pieces (us, pt)) ^ from;

            while (b)
            {
                Square s = pop_lsb (&b);
                if (!pos.legal (make_move (s, to), pos.pinned_pieces (us)))
                    others ^= s;
            }

            if (!others)
            { /* Disambiguation is not needed */
            }

            else if (!(others & file_bb (from)))
                san += to_char (file_of (from));

            else if (!(others & rank_bb (from)))
                san += to_char (rank_of (from));

            else
            {
                san += to_char (file_of (from));
                san += to_char (rank_of (from));
            }
        } else if (pos.capture (m))
            san = to_char (file_of (from));

        if (pos.capture (m))
            san += 'x';

        san += to_char (file_of (to));
        san += to_char (rank_of (to));

        if (type_of (m) == PROMOTION)
            san += string ("=") + PieceToChar[WHITE][promotion_type (m)];
    }

    if (pos.gives_check (m, CheckInfo (pos)))
    {
        StateInfo st;
        pos.do_move (m, st);
        san += MoveList<LEGAL> (pos).size () ? "+" : "#";
        pos.undo_move (m);
    }

    return san;
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
