# Automatically generated makefile, created by the Introjucer
# Don't edit this file! Your changes will be overwritten when you re-save the Introjucer project!

# (this disables dependency generation if multiple architectures are set)
DEPFLAGS := $(if $(word 2, $(TARGET_ARCH)), , -MMD)

ifndef CONFIG
  CONFIG=Debug
endif

ifeq ($(CONFIG),Debug)
  BINDIR := build
  LIBDIR := build
  OBJDIR := build/intermediate/Debug
  OUTDIR := build

  ifeq ($(TARGET_ARCH),)
    TARGET_ARCH := -march=native
  endif

  CPPFLAGS := $(DEPFLAGS) -D "LINUX=1" -D "DEBUG=1" -D "_DEBUG=1" -D "JUCER_LINUX_MAKE_6D53C8B4=1" -D "JUCE_APP_VERSION=1.0.0" -D "JUCE_APP_VERSION_HEX=0x10000" -I /usr/include -I /usr/include/freetype2 -I ../../JuceLibraryCode -I ../../../../Dev/JUCE-WINDOWS/modules
  CFLAGS += $(CPPFLAGS) $(TARGET_ARCH) -g -ggdb -O0
  CXXFLAGS += $(CFLAGS) -std=c++11
  LDFLAGS += $(TARGET_ARCH) -L$(BINDIR) -L$(LIBDIR) -L/usr/X11R6/lib/ -lGL -lX11 -lXext -lXinerama -ldl -lfreetype -lpthread -lrt 

  TARGET := OpenChess
  BLDCMD = $(CXX) -o $(OUTDIR)/$(TARGET) $(OBJECTS) $(LDFLAGS) $(RESOURCES) $(TARGET_ARCH)
  CLEANCMD = rm -rf $(OUTDIR)/$(TARGET) $(OBJDIR)
endif

ifeq ($(CONFIG),Release)
  BINDIR := build
  LIBDIR := build
  OBJDIR := build/intermediate/Release
  OUTDIR := build

  ifeq ($(TARGET_ARCH),)
    TARGET_ARCH := -march=native
  endif

  CPPFLAGS := $(DEPFLAGS) -D "LINUX=1" -D "NDEBUG=1" -D "JUCER_LINUX_MAKE_6D53C8B4=1" -D "JUCE_APP_VERSION=1.0.0" -D "JUCE_APP_VERSION_HEX=0x10000" -I /usr/include -I /usr/include/freetype2 -I ../../JuceLibraryCode -I ../../../../Dev/JUCE-WINDOWS/modules
  CFLAGS += $(CPPFLAGS) $(TARGET_ARCH) -O3
  CXXFLAGS += $(CFLAGS) -std=c++11
  LDFLAGS += $(TARGET_ARCH) -L$(BINDIR) -L$(LIBDIR) -fvisibility=hidden -L/usr/X11R6/lib/ -lGL -lX11 -lXext -lXinerama -ldl -lfreetype -lpthread -lrt 

  TARGET := OpenChess
  BLDCMD = $(CXX) -o $(OUTDIR)/$(TARGET) $(OBJECTS) $(LDFLAGS) $(RESOURCES) $(TARGET_ARCH)
  CLEANCMD = rm -rf $(OUTDIR)/$(TARGET) $(OBJDIR)
endif

OBJECTS := \
  $(OBJDIR)/BoardComponent_478788c0.o \
  $(OBJDIR)/BoardTabbedComponent_eaf6e8d4.o \
  $(OBJDIR)/BoardTabsComponent_941a2ae2.o \
  $(OBJDIR)/MainContentComponent_19da5e66.o \
  $(OBJDIR)/Main_90ebc5c2.o \
  $(OBJDIR)/MainWindow_499ac812.o \
  $(OBJDIR)/bitbase_1b2588be.o \
  $(OBJDIR)/bitboard_58bb85e3.o \
  $(OBJDIR)/misc_90c689d6.o \
  $(OBJDIR)/movegen_c0dea0bf.o \
  $(OBJDIR)/position_56a7513.o \
  $(OBJDIR)/uci_b1803dfb.o \
  $(OBJDIR)/game_c810c45b.o \
  $(OBJDIR)/BinaryData_ce4232d4.o \
  $(OBJDIR)/juce_audio_basics_823af92c.o \
  $(OBJDIR)/juce_audio_formats_938dfc8a.o \
  $(OBJDIR)/juce_core_26d35a0e.o \
  $(OBJDIR)/juce_data_structures_61cb2f4a.o \
  $(OBJDIR)/juce_events_97ee0f82.o \
  $(OBJDIR)/juce_graphics_9b1b5de6.o \
  $(OBJDIR)/juce_gui_basics_be516262.o \
  $(OBJDIR)/juce_gui_extra_650cc46a.o \
  $(OBJDIR)/juce_opengl_583637ae.o \

.PHONY: clean

$(OUTDIR)/$(TARGET): $(OBJECTS) $(RESOURCES)
	@echo Linking OpenChess
	-@mkdir -p $(BINDIR)
	-@mkdir -p $(LIBDIR)
	-@mkdir -p $(OUTDIR)
	@$(BLDCMD)

clean:
	@echo Cleaning OpenChess
	@$(CLEANCMD)

strip:
	@echo Stripping OpenChess
	-@strip --strip-unneeded $(OUTDIR)/$(TARGET)

$(OBJDIR)/BoardComponent_478788c0.o: ../../Source/BoardComponent.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling BoardComponent.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/BoardTabbedComponent_eaf6e8d4.o: ../../Source/BoardTabbedComponent.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling BoardTabbedComponent.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/BoardTabsComponent_941a2ae2.o: ../../Source/BoardTabsComponent.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling BoardTabsComponent.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/MainContentComponent_19da5e66.o: ../../Source/MainContentComponent.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling MainContentComponent.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/Main_90ebc5c2.o: ../../Source/Main.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling Main.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/MainWindow_499ac812.o: ../../Source/MainWindow.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling MainWindow.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/bitbase_1b2588be.o: ../../Source/BoardPosition/stockfish/bitbase.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling bitbase.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/bitboard_58bb85e3.o: ../../Source/BoardPosition/stockfish/bitboard.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling bitboard.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/misc_90c689d6.o: ../../Source/BoardPosition/stockfish/misc.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling misc.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/movegen_c0dea0bf.o: ../../Source/BoardPosition/stockfish/movegen.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling movegen.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/position_56a7513.o: ../../Source/BoardPosition/stockfish/position.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling position.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/uci_b1803dfb.o: ../../Source/BoardPosition/stockfish/uci.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling uci.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/game_c810c45b.o: ../../Source/BoardPosition/game.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling game.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/BinaryData_ce4232d4.o: ../../JuceLibraryCode/BinaryData.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling BinaryData.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_audio_basics_823af92c.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_audio_basics/juce_audio_basics.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_audio_basics.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_audio_formats_938dfc8a.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_audio_formats/juce_audio_formats.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_audio_formats.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_core_26d35a0e.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_core/juce_core.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_core.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_data_structures_61cb2f4a.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_data_structures/juce_data_structures.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_data_structures.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_events_97ee0f82.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_events/juce_events.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_events.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_graphics_9b1b5de6.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_graphics/juce_graphics.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_graphics.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_gui_basics_be516262.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_gui_basics/juce_gui_basics.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_gui_basics.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_gui_extra_650cc46a.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_gui_extra/juce_gui_extra.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_gui_extra.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

$(OBJDIR)/juce_opengl_583637ae.o: ../../../../Dev/JUCE-WINDOWS/modules/juce_opengl/juce_opengl.cpp
	-@mkdir -p $(OBJDIR)
	@echo "Compiling juce_opengl.cpp"
	@$(CXX) $(CXXFLAGS) -o "$@" -c "$<"

-include $(OBJECTS:%.o=%.d)
