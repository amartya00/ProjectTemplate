cmake_minimum_required(VERSION 3.0)

project(TestProject)

set (CMAKE_CXX_STANDARD 11)

# Set header paths
set(PACKAGE_HEADERS ${PACKAGE_CACHE}/headers)
set(HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/headers)

# Add the lib folder for compilation
add_subdirectory(lib)