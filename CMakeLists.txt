#CMakeLists.txt

cmake_minimum_required(VERSION 3.0)

# Set up the project
project(UtilsApp)

set(SRC "${CMAKE_CURRENT_SOURCE_DIR}")
set(DEST "${CMAKE_CURRENT_BINARY_DIR}/Project")
set(INSTALL "/opt/MyApps/")

add_custom_target(default ALL
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/bin" "${DEST}/bin" "EXEC"
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/libs" "${DEST}/libs" "NOEXEC"
    COMMAND ${CMAKE_COMMAND} -P "${SRC}/CopySrc.cmake" "${SRC}/autocompletes" "${DEST}/autocompletes" "NOEXEC")

install(DIRECTORY ${DEST} DESTINATION ${INSTALL} USE_SOURCE_PERMISSIONS)
