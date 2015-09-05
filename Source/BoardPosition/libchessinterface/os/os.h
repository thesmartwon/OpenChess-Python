
// chessinterfacelib, a library to run chess engines
// Copyright (C) 2012  Jonas Thiem
//
// chessinterfacelib is free software: you can redistribute it and/or
// modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation, either version 3 of
// the License, or (at your option) any later version.
//
// chessinterfacelib is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with chessinterfacelib in a file named COPYING.txt.
// If not, see <http://www.gnu.org/licenses/>.

// various operating system detections (at compile time):

#ifndef WINDOWS
#if defined(WIN32) || defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(_MSC_VER)
#define WINDOWS
#ifdef _WIN32_WINNT
#undef _WIN32_WINNT
#endif
#define _WIN32_WINNT 0x0501
#if defined __MINGW_H
#define _WIN32_IE 0x0400
#endif
#endif
#endif

#ifndef LINUX
#if defined(linux__) || defined(__linux) || defined(__linux__) || defined(linux)
#define LINUX
#endif
#endif

#ifndef MAC
#if defined(__APPLE__) && defined(__MACH__)
#define MAC
#endif
#endif

#ifndef UNIX
#if (defined(MAC) || defined(LINUX))
#define UNIX
#endif
#endif


