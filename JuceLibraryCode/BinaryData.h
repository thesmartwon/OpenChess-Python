/* =========================================================================================

   This is an auto-generated file: Any edits you make may be overwritten!

*/

#ifndef BINARYDATA_H_120090431_INCLUDED
#define BINARYDATA_H_120090431_INCLUDED

namespace BinaryData
{
    extern const char*   board_jpg;
    const int            board_jpgSize = 8818;

    extern const char*   Chess_Pieces_Sprite_png;
    const int            Chess_Pieces_Sprite_pngSize = 114179;

    // Points to the start of a list of resource names.
    extern const char* namedResourceList[];

    // Number of elements in the namedResourceList array.
    const int namedResourceListSize = 2;

    // If you provide the name of one of the binary resource variables above, this function will
    // return the corresponding data and its size (or a null pointer if the name isn't found).
    const char* getNamedResource (const char* resourceNameUTF8, int& dataSizeInBytes) throw();
}

#endif
