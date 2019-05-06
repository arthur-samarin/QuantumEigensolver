cmake_minimum_required(VERSION 3.10)
project(cvqe)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Eigen3
find_package(Eigen3 3.0 REQUIRED)

# CMA-ES
find_package(PkgConfig)
pkg_check_modules(PC_CMAES REQUIRED libcmaes)
find_library(CMAES_LIBRARY NAMES cmaes HINTS ${PC_CMAES_LIBDIR} ${PC_CMAES_LIBRARY_DIRS} )
include_directories(${PC_CMAES_INCLUDE_DIRS})
link_libraries(${CMAES_LIBRARY})

# glog
find_package(PkgConfig)
pkg_check_modules(PC_GLOG REQUIRED libglog)
find_library(GLOG_LIBRARY NAMES glog HINTS ${PC_GLOG_LIBDIR} ${PC_GLOG_LIBRARY_DIRS} )
include_directories(${PC_GLOG_INCLUDE_DIRS})
link_libraries(${GLOG_LIBRARY})

# QuEST
include_directories(QuEST)

# Python
find_package (Python 3 COMPONENTS Interpreter Development)
include_directories(${Python_INCLUDE_DIRS})
link_libraries(${Python_LIBRARIES})

# Boost.Python
find_package(Boost REQUIRED COMPONENTS python3 numpy3)
include_directories(${Boost_INCLUDE_DIRS})
link_libraries(${Boost_LIBRARIES})

# Compilation options
set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")
set(CMAKE_INCLUDE_SYSTEM_FLAG_CXX "-isystem")

# What to build
include_directories(src)
file(GLOB quest_SRC QuEST/*.c QuEST/CPU/QuEST_cpu.c QuEST/CPU/QuEST_cpu_local.c)
set(CVQE_SRC ${quest_SRC} src/qcirc.h src/qcirc.cpp src/vqe.cpp src/vqe.h src/gates/basic.h src/gates/all.h src/gates/block_a.h src/py/python_cvqe.cpp src/py/eigen_numpy.cpp)
add_library(cvqe SHARED ${CVQE_SRC})
set_target_properties(
        cvqe
        PROPERTIES
        PREFIX ""
        OUTPUT_NAME "cvqe"
        LINKER_LANGUAGE C
)

add_executable(cvqe_benchmarks ${CVQE_SRC} src/main_benchmarks.cpp)
add_executable(cvqe_pytest ${CVQE_SRC} src/main_pytest.cpp)