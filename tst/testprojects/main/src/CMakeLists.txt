cmake_minimum_required(VERSION 3.0)

include_directories(${HEADERS})
include_directories(${PACKAGE_HEADERS})

add_executable(main.out binm.cc)

target_link_libraries(main.out ${A} ${B} ${K})

install(TARGETS main.out DESTINATION bin)

