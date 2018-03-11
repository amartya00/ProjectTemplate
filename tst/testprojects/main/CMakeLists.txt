cmake_minimum_required(VERSION 3.0)
project(BuildetTest)

# Check is PackageCache var is set
set(PACKAGE_HEADERS ${PACKAGE_CACHE}/headers)
set(HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/headers)
set(SRC ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Find dependent libraries
find_library(K NAMES k PATHS ${PACKAGE_CACHE}/lib NO_DEFAULT_PATH NO_CMAKE_SYSTEM_PATH)
find_library(A NAMES a PATHS ${PACKAGE_CACHE}/lib NO_DEFAULT_PATH NO_CMAKE_SYSTEM_PATH)
find_library(B NAMES b PATHS ${PACKAGE_CACHE}/lib NO_DEFAULT_PATH NO_CMAKE_SYSTEM_PATH)

find_library(K NAMES k PATHS ${PACKAGE_CACHE}/lib)
find_library(A NAMES a PATHS ${PACKAGE_CACHE}/lib)
find_library(B NAMES b PATHS ${PACKAGE_CACHE}/lib)

add_subdirectory(${SRC})
enable_testing()
