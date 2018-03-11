cmake_minimum_required(VERSION 3.0)
project(BuildetTest)

# Check is PackageCache var is set
set(PACKAGE_HEADERS ${PACKAGE_CACHE}/headers)
set(HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/headers)
set(LIBSRC ${CMAKE_CURRENT_SOURCE_DIR}/lib)

# Find dependent libraries
find_library(K NAMES k PATHS ${PACKAGE_CACHE}/lib NO_DEFAULT_PATH NO_CMAKE_SYSTEM_PATH)
find_library(K NAMES k PATHS ${PACKAGE_CACHE}/lib)

message(STATUS "Hello world!")
message(STATUS ${K})
enable_testing()

add_subdirectory(${LIBSRC})

