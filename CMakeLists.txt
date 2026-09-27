cmake_minimum_required(VERSION 3.20)
project(tantric_engine VERSION 1.0.0 LANGUAGES C CXX)

# C++20 Standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler Flags
add_compile_options(
    -O3
    -march=native
    -Wall
    -Wextra
    -Wpedantic
    -pipe
    -fPIC
)

# Include Directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/sweph
)

# Link Directories
link_directories(${CMAKE_CURRENT_SOURCE_DIR}/third_party/sweph)

# Find required packages
find_package(Threads REQUIRED)

# Optional: OpenCV (for vision pipeline)
find_package(OpenCV QUIET)
if(OpenCV_FOUND)
    message(STATUS "OpenCV found: ${OpenCV_VERSION}")
    add_definitions(-DHAS_OPENCV)
else()
    message(STATUS "OpenCV not found - vision pipeline disabled")
endif()

# Optional: MySQL Client
find_library(MYSQL_CLIENT mysqlclient PATHS /usr/lib/x86_64-linux-gnu)
if(MYSQL_CLIENT)
    message(STATUS "MySQL client library found")
    add_definitions(-DHAS_MYSQL)
else()
    message(STATUS "MySQL client not found - database features disabled")
endif()

# Main Executable
add_executable(tantric_engine
    src/main.cpp
    src/ephemeris_engine.cpp
    src/yantra_engine.cpp
    src/sound_weaver.cpp
    src/safety_validator.cpp
)

# Link Libraries
target_link_libraries(tantric_engine
    PRIVATE
    Threads::Threads
    m  # math library
)

# Link Swiss Ephemeris if available
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sweph/libswe.a")
    target_link_libraries(tantric_engine PRIVATE swe)
    target_compile_definitions(tantric_engine PRIVATE HAS_SWEPH)
    message(STATUS "Swiss Ephemeris library found")
else()
    message(WARNING "Swiss Ephemeris not found - ephemeris engine disabled")
endif()

# Link OpenCV if available
if(OpenCV_FOUND)
    target_link_libraries(tantric_engine PRIVATE ${OpenCV_LIBS})
endif()

# Link MySQL if available
if(MYSQL_CLIENT)
    target_link_libraries(tantric_engine PRIVATE ${MYSQL_CLIENT})
endif()

# Install
install(TARGETS tantric_engine DESTINATION bin)
