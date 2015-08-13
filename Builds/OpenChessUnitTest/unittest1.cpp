#include "stdafx.h"
#include "CppUnitTest.h"
#include "../../Source/BoardPosition/game.h"

using namespace Microsoft::VisualStudio::CppUnitTestFramework;

namespace OpenChessUnitTest
{		
	TEST_CLASS(UnitTest1)
	{
	public:
		
		TEST_METHOD(TestMethod1)
		{
            Game game;
            if (!game.hasRootNode ())
                game.appendMoveToMainline (new MoveNode (nullptr, nullptr, Stockfish::make_move (Stockfish::Square::SQ_E2, Stockfish::Square::SQ_E4), ""));
            game.appendMoveToMainline (new MoveNode (nullptr, nullptr, Stockfish::make_move (Stockfish::Square::SQ_D7, Stockfish::Square::SQ_D5), ""));

			// TODO: Your test code here
            Assert::IsNotNull (&game, L"Kappa");
		}

	};
}