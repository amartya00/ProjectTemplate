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
