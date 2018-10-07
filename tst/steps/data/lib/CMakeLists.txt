cmake_minimum_required(VERSION 3.0)

include_directories(${HEADERS})
include_directories(${PACKAGE_HEADERS})

add_executable(myapp test.cc)
add_library(test SHARED test.cc)

install(TARGETS myapp DESTINATION bin)