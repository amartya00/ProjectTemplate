Feature: CPP workflow
  As a user of the Cpp workflow,
  I want to test successful building, testing and packaging of a cpp application

  Background:
    Given I have a C++ project with a proper md.json file.

  Scenario: C++ build workflow happy case.
    When I run the c++ build workflow.
    And I run the packaging step.
    Then I should have the build folder.
    And It should contain a file called test.tar .
    And It should contain a file called test-headers.tar .
    And It should contain a file with prefix myapp and suffix .snap .
    And the test-headers.tar should contain the following files.
        |Files         |
        |CMakeLists.txt|
        |md.json       |
        |test          |
        |test/test.h   |
    And the test.tar should contain the following files.
        |Files         |
        |CMakeLists.txt|
        |md.json       |
        |libtest.so    |
    And the md.json in the test.tar should contain the following dependencies:
        |Name     |Version|
        |a-headers|0.1    |
        |b-headers|0.1    |
    And the md.json in the test-headers.tar should contain the following dependencies:
        |Name     |Version|
        |a-headers|0.1    |
        |b-headers|0.1    |
