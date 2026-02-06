CXX ?= clang++
PKG_CONFIG ?= pkg-config

CXXFLAGS += -std=c++17 -O2 -Wall -Wextra -DFLOW_VK_STANDALONE

VULKAN_CFLAGS := $(shell $(PKG_CONFIG) --cflags vulkan)
VULKAN_LIBS := $(shell $(PKG_CONFIG) --libs vulkan)
GLFW_CFLAGS := $(shell $(PKG_CONFIG) --cflags glfw3)
GLFW_LIBS := $(shell $(PKG_CONFIG) --libs glfw3)

SHADER_COMPILER ?= glslangValidator

TARGET := vulkan_scene
SRC := main.cpp

VERT_SPV := shaders/scene.vert.spv
FRAG_SPV := shaders/scene.frag.spv

RPATHS := /opt/homebrew/opt/vulkan-loader/lib /opt/homebrew/opt/molten-vk/lib /opt/homebrew/opt/vulkan-validationlayers/lib
RPATH_FLAGS := $(foreach p,$(RPATHS),-Wl,-rpath,$(p))
FRAMEWORKS := -framework CoreGraphics -framework ImageIO -framework CoreFoundation

.PHONY: all clean shaders run

all: shaders $(TARGET)

$(TARGET): $(SRC) $(VERT_SPV) $(FRAG_SPV)
	$(CXX) $(CXXFLAGS) $(VULKAN_CFLAGS) $(GLFW_CFLAGS) -o $@ $(SRC) $(VULKAN_LIBS) $(GLFW_LIBS) $(FRAMEWORKS) $(RPATH_FLAGS)

shaders: $(VERT_SPV) $(FRAG_SPV)

$(VERT_SPV): shaders/scene.vert
	$(SHADER_COMPILER) -V $< -o $@

$(FRAG_SPV): shaders/scene.frag
	$(SHADER_COMPILER) -V $< -o $@

run: all
	./run.sh

clean:
	rm -f $(TARGET) $(VERT_SPV) $(FRAG_SPV)
