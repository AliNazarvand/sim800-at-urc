cmake_minimum_required(VERSION 3.16)
project(sim800_at_urc_db LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Header-only interface target
add_library(sim800_at INTERFACE)
target_include_directories(sim800_at INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/sim800_at
)

enable_testing()

add_executable(test_database tests/test_at_db.cpp)
target_link_libraries(test_database PRIVATE sim800_at)
add_test(NAME database COMMAND test_database)