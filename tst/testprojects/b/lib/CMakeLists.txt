cmake_minimum_required(VERSION 3.0)

include_directories(${HEADERS})
include_directories(${PACKAGE_HEADERS})

add_library(b SHARED libb.cc)

target_link_libraries(b ${K})
