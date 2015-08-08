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
    template<CastlingRight Cr, bool Checks, bool Chess960>
    ExtMove* generate_castling (const Position& pos, ExtMove* moveList, Color us, const CheckInfo* ci)
    {

        static const bool KingSide = (Cr == WHITE_OO || Cr == BLACK_OO);

        if (pos.castling_impeded (Cr) || !pos.can_castle (Cr))
            return moveList;

        // After castling, the rook and king final positions are the same in Chess960
        // as they would be in standard chess.
        Square kfrom = pos.king_square (us);
        Square rfrom = pos.castling_rook_square (Cr);
        Square kto = relative_square (us, KingSide ? SQ_G1 : SQ_C1);
        Bitboard enemies = pos.pieces (~us);

        assert (!pos.checkers ());

        const Square K = Chess960 ? kto > kfrom ? DELTA_W : DELTA_E
            : KingSide ? DELTA_W : DELTA_E;

        for (Square s = kto; s != kfrom; s += K)
            if (pos.attackers_to (s) & enemies)
            return moveList;

        // Because we generate only legal castling moves we need to verify that
        // when moving the castling rook we do not discover some hidden checker.
        // For instance an enemy queen in SQ_A1 when castling rook is in SQ_B1.
        if (Chess960 && (attacks_bb<ROOK> (kto, pos.pieces () ^ rfrom) & pos.pieces (~us, ROOK, QUEEN)))
            return moveList;

        Move m = make<CASTLING> (kfrom, rfrom);

        if (Checks && !pos.gives_check (m, *ci))
            return moveList;

        (moveList++)->move = m;

        return moveList;
    }


    template<GenType Type, Square Delta>
    inline ExtMove* make_promotions (ExtMove* moveList, Square to, const CheckInfo* ci)
    {

        if (Type == CAPTURES || Type == EVASIONS || Type == NON_EVASIONS)
            (moveList++)->move = make<PROMOTION> (to - Delta, to, QUEEN);

        if (Type == QUIETS || Type == EVASIONS || Type == NON_EVASIONS)
        {
            (moveList++)->move = make<PROMOTION> (to - Delta, to, ROOK);
            (moveList++)->move = make<PROMOTION> (to - Delta, to, BISHOP);
            (moveList++)->move = make<PROMOTION> (to - Delta, to, KNIGHT);
        }

        // Knight promotion is the only promotion that can give a direct check
        // that's not already included in the queen promotion.
        if (Type == QUIET_CHECKS && (StepAttacksBB[W_KNIGHT][to] & ci->ksq))
            (moveList++)->move = make<PROMOTION> (to - Delta, to, KNIGHT);
        else
            (void)ci; // Silence a warning under MSVC

        return moveList;
    }


    template<Color Us, GenType Type>
    ExtMove* generate_pawn_moves (const Position& pos, ExtMove* moveList,
        Bitboard target, const CheckInfo* ci)
    {

        // Compute our parametrized parameters at compile time, named according to
        // the point of view of white side.
        const Color    Them = (Us == WHITE ? BLACK : WHITE);
        const Bitboard TRank8BB = (Us == WHITE ? Rank8BB : Rank1BB);
        const Bitboard TRank7BB = (Us == WHITE ? Rank7BB : Rank2BB);
        const Bitboard TRank3BB = (Us == WHITE ? Rank3BB : Rank6BB);
        const Square   Up = (Us == WHITE ? DELTA_N : DELTA_S);
        const Square   Right = (Us == WHITE ? DELTA_NE : DELTA_SW);
        const Square   Left = (Us == WHITE ? DELTA_NW : DELTA_SE);

        Bitboard emptySquares;

        Bitboard pawnsOn7 = pos.pieces (Us, PAWN) &  TRank7BB;
        Bitboard pawnsNotOn7 = pos.pieces (Us, PAWN) & ~TRank7BB;

        Bitboard enemies = (Type == EVASIONS ? pos.pieces (Them) & target :
            Type == CAPTURES ? target : pos.pieces (Them));

        // Single and double pawn pushes, no promotions
        if (Type != CAPTURES)
        {
            emptySquares = (Type == QUIETS || Type == QUIET_CHECKS ? target : ~pos.pieces ());

            Bitboard b1 = shift_bb<Up> (pawnsNotOn7)   & emptySquares;
            Bitboard b2 = shift_bb<Up> (b1 & TRank3BB) & emptySquares;

            if (Type == EVASIONS) // Consider only blocking squares
            {
                b1 &= target;
                b2 &= target;
            }

            if (Type == QUIET_CHECKS)
            {
                b1 &= pos.attacks_from<PAWN> (ci->ksq, Them);
                b2 &= pos.attacks_from<PAWN> (ci->ksq, Them);

                // Add pawn pushes which give discovered check. This is possible only
                // if the pawn is not on the same file as the enemy king, because we
                // don't generate captures. Note that a possible discovery check
                // promotion has been already generated amongst the captures.
                if (pawnsNotOn7 & ci->dcCandidates)
                {
                    Bitboard dc1 = shift_bb<Up> (pawnsNotOn7 & ci->dcCandidates) & emptySquares & ~file_bb (ci->ksq);
                    Bitboard dc2 = shift_bb<Up> (dc1 & TRank3BB) & emptySquares;

                    b1 |= dc1;
                    b2 |= dc2;
                }
            }

            while (b1)
            {
                Square to = pop_lsb (&b1);
                (moveList++)->move = make_move (to - Up, to);
            }

            while (b2)
            {
                Square to = pop_lsb (&b2);
                (moveList++)->move = make_move (to - Up - Up, to);
            }
        }

        // Promotions and underpromotions
        if (pawnsOn7 && (Type != EVASIONS || (target & TRank8BB)))
        {
            if (Type == CAPTURES)
                emptySquares = ~pos.pieces ();

            if (Type == EVASIONS)
                emptySquares &= target;

            Bitboard b1 = shift_bb<Right> (pawnsOn7) & enemies;
            Bitboard b2 = shift_bb<Left > (pawnsOn7) & enemies;
            Bitboard b3 = shift_bb<Up   > (pawnsOn7) & emptySquares;

            while (b1)
                moveList = make_promotions<Type, Right> (moveList, pop_lsb (&b1), ci);

            while (b2)
                moveList = make_promotions<Type, Left > (moveList, pop_lsb (&b2), ci);

            while (b3)
                moveList = make_promotions<Type, Up   > (moveList, pop_lsb (&b3), ci);
        }

        // Standard and en-passant captures
        if (Type == CAPTURES || Type == EVASIONS || Type == NON_EVASIONS)
        {
            Bitboard b1 = shift_bb<Right> (pawnsNotOn7) & enemies;
            Bitboard b2 = shift_bb<Left > (pawnsNotOn7) & enemies;

            while (b1)
            {
                Square to = pop_lsb (&b1);
                (moveList++)->move = make_move (to - Right, to);
            }

            while (b2)
            {
                Square to = pop_lsb (&b2);
                (moveList++)->move = make_move (to - Left, to);
            }

            if (pos.ep_square () != SQ_NONE)
            {
                assert (rank_of (pos.ep_square ()) == relative_rank (Us, RANK_6));

                // An en passant capture can be an evasion only if the checking piece
                // is the double pushed pawn and so is in the target. Otherwise this
                // is a discovery check and we are forced to do otherwise.
                if (Type == EVASIONS && !(target & (pos.ep_square () - Up)))
                    return moveList;

                b1 = pawnsNotOn7 & pos.attacks_from<PAWN> (pos.ep_square (), Them);

                assert (b1);

                while (b1)
                    (moveList++)->move = make<ENPASSANT> (pop_lsb (&b1), pos.ep_square ());
            }
        }

        return moveList;
    }


    template<PieceType Pt, bool Checks> FORCE_INLINE
        ExtMove* generate_moves (const Position& pos, ExtMove* moveList, Color us,
            Bitboard target, const CheckInfo* ci)
    {

        assert (Pt != KING && Pt != PAWN);

        const Square* pl = pos.list<Pt> (us);

        for (Square from = *pl; from != SQ_NONE; from = *++pl)
        {
            if (Checks)
            {
                if ((Pt == BISHOP || Pt == ROOK || Pt == QUEEN)
                    && !(PseudoAttacks[Pt][from] & target & ci->checkSq[Pt]))
                    continue;

                if (ci->dcCandidates && (ci->dcCandidates & from))
                    continue;
            }

            Bitboard b = pos.attacks_from<Pt> (from) & target;

            if (Checks)
                b &= ci->checkSq[Pt];

            while (b)
                (moveList++)->move = make_move (from, pop_lsb (&b));
        }

        return moveList;
    }


    template<Color Us, GenType Type> FORCE_INLINE
        ExtMove* generate_all (const Position& pos, ExtMove* moveList, Bitboard target,
            const CheckInfo* ci = NULL)
    {

        const bool Checks = Type == QUIET_CHECKS;

        moveList = generate_pawn_moves<Us, Type> (pos, moveList, target, ci);
        moveList = generate_moves<KNIGHT, Checks> (pos, moveList, Us, target, ci);
        moveList = generate_moves<BISHOP, Checks> (pos, moveList, Us, target, ci);
        moveList = generate_moves<  ROOK, Checks> (pos, moveList, Us, target, ci);
        moveList = generate_moves< QUEEN, Checks> (pos, moveList, Us, target, ci);

        if (Type != QUIET_CHECKS && Type != EVASIONS)
        {
            Square ksq = pos.king_square (Us);
            Bitboard b = pos.attacks_from<KING> (ksq) & target;
            while (b)
                (moveList++)->move = make_move (ksq, pop_lsb (&b));
        }

        if (Type != CAPTURES && Type != EVASIONS && pos.can_castle (Us))
        {
            if (pos.is_chess960 ())
            {
                moveList = generate_castling<MakeCastling<Us, KING_SIDE>::right, Checks, true> (pos, moveList, Us, ci);
                moveList = generate_castling<MakeCastling<Us, QUEEN_SIDE>::right, Checks, true> (pos, moveList, Us, ci);
            } else
            {
                moveList = generate_castling<MakeCastling<Us, KING_SIDE>::right, Checks, false> (pos, moveList, Us, ci);
                moveList = generate_castling<MakeCastling<Us, QUEEN_SIDE>::right, Checks, false> (pos, moveList, Us, ci);
            }
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
	for (int i = 0; i < 250; ++i)
    {
		if (moveList[i].move == MOVE_NULL)
			break;
        else if (to_sq(moveList[i].move) == to_sq(m))
        {
            if (!foundOne)
                foundOne = true;
            else
                return true;
        }
    }
    return false;
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
        p.undo_move (m);
        // is it a capture?
        if (p.piece_on (to_sq (m)) != Stockfish::Piece::NO_PIECE)
            moveTextAfter = moveTextBefore[0] + "x";
        p.do_move (m, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));

        // dxc8=Q
        moveTextAfter += moveTextBefore.substr (2, 4) + "=" + (char)(toupper(moveTextBefore[5]));
    }
    else //normal move
    {
        if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::BISHOP)
        {
            moveTextAfter = "B" + moveTextBefore.substr(2, 4);
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::KNIGHT)
        {
            moveTextAfter = "N";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NULL };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<KNIGHT, true> (tmpPos, moveListPtr, p.side_to_move (), 0, chkInfo);
            if (containsTwo (moveListPtr, m))
                moveTextAfter += moveTextBefore.substr(0, 1);
            p.do_move (m, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
			moveTextAfter += moveTextBefore.substr(2, 4);
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::ROOK)
        {
            moveTextAfter = "R";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NULL };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<ROOK, true> (tmpPos, moveListPtr, p.side_to_move (), 0, chkInfo);
            if (containsTwo (moveListPtr, m))
                moveTextAfter += moveTextBefore.substr(0, 1);
            p.do_move (m, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
        }
        else if (type_of (p.piece_on (to_sq (m))) == Stockfish::PieceType::QUEEN)
        {
            moveTextAfter = "Q";
            // if two of the same piece can go to the same square, we have to fix this ambiguity
            p.undo_move (m);
            ExtMove moveList[250] = { Stockfish::Move::MOVE_NULL };
            ExtMove* moveListPtr = moveList;
            const Stockfish::Position tmpPos = Stockfish::Position (p);
            const Stockfish::CheckInfo* chkInfo = &Stockfish::CheckInfo (tmpPos);
            moveListPtr = MoveGen::generate_moves<QUEEN, true> (tmpPos, moveListPtr, p.side_to_move (), 0, chkInfo);
            if (containsTwo (moveListPtr, m))
                moveTextAfter += moveTextBefore.substr(0, 1);
            p.do_move (m, *(Stockfish::StateInfo *)calloc (1, sizeof (Stockfish::StateInfo)));
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
            p.do_move (m, st);
        }
		return moveTextAfter;
    }
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
