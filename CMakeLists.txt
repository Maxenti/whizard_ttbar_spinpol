cmake_minimum_required(VERSION 3.20)
project(whizard_ttbar_qis VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(QIS_BUILD_SHOWER "Build the PYTHIA8 to HepMC3 shower executable" ON)
option(QIS_ENABLE_WARNINGS "Enable strict compiler warnings" ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

if(QIS_BUILD_SHOWER)
  find_package(Pythia8 REQUIRED)
  find_package(HepMC3 REQUIRED)

  add_library(qis_shower_support
    src/qis/ShowerConfig.cc
    src/qis/EventMetadata.cc
  )
  target_include_directories(qis_shower_support PUBLIC include)
  target_link_libraries(qis_shower_support PUBLIC Pythia8::Pythia8 HepMC3::HepMC3)

  add_executable(qis_lhe_to_hepmc3 src/qis/lhe_to_hepmc3.cc)
  target_link_libraries(qis_lhe_to_hepmc3 PRIVATE qis_shower_support)

  if(QIS_ENABLE_WARNINGS)
    foreach(target qis_shower_support qis_lhe_to_hepmc3)
      target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic -Wshadow -Wconversion)
    endforeach()
  endif()

  install(TARGETS qis_lhe_to_hepmc3 RUNTIME DESTINATION bin)
endif()
