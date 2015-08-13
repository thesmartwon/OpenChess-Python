
// libchessinterface, a library to run chess engines
// Copyright (C) 2012  Jonas Thiem
//
// libchessinterface is free software: you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of
// the License, or (at your option) any later version.
//
// libchessinterface is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with libchessinterface in a file named COPYING.txt.
// If not, see <http://www.gnu.org/licenses/>.

#ifndef FILE_FILE_H_
#define FILE_FILE_H_

int file_Cwd(const char* path);

char* file_GetCwd();

char* file_GetAbsolutePathFromRelativePath(const char* path);

int file_DoesFileExist(const char* path);

int file_IsDirectory(const char* path);

int file_IsPathRelative(const char* path);

char* file_GetDirectoryPathFromFilePath(const char* path);

char* file_GetAbsoluteDirectoryPathFromFilePath(const char* path);

char* file_GetFileNameFromFilePath(const char* path);

int file_ContentToBuffer(const char* path, char** buf, size_t* buflen);

char* file_AddComponentToPath(const char* path, const char* component);

void file_StripComponentFromPath(char* path);

void file_MakeSlashesNative(char* path);

char* file_GetUserFileDir();

char* file_GetTempPath(const char* name);

#endif  // FILE_FILE_H_

