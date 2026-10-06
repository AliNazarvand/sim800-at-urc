cmake_minimum_required(VERSION 3.16)
project(sim800_at_urc_db LANGUAGES CXX VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(SIM800_AT_BUILD_TESTS "Build host-side tests" ON)

# Header-only interface library
add_library(sim800_at INTERFACE)
add_library(sim800_at::sim800_at ALIAS sim800_at)
target_include_directories(sim800_at INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# pkg-config
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/sim800_at.pc.in
    ${CMAKE_CURRENT_BINARY_DIR}/sim800_at.pc
    @ONLY
)

# Install
install(TARGETS sim800_at EXPORT sim800_atTargets)
install(DIRECTORY include/ DESTINATION include)
install(EXPORT sim800_atTargets DESTINATION lib/cmake/sim800_at)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/sim800_at.pc DESTINATION lib/pkgconfig)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE
        DESTINATION share/doc/sim800_at_urc_db)

# Tests (no external test framework, no FetchContent)
if(SIM800_AT_BUILD_TESTS)
    enable_testing()
    add_executable(test_database tests/test_at_db.cpp)
    target_link_libraries(test_database PRIVATE sim800_at)
    add_test(NAME database COMMAND test_database)
endif()