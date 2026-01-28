Feature: Transfers

  Scenario: User is able to make a standard transfer between two accounts
    Given Account registry is empty
    And I create an account using name: "john", last name: "lennon", pesel: "40100912345"
    And I create an account using name: "paul", last name: "mccartney", pesel: "42061812876"
    And Account with pesel "40100912345" has balance of "1000.0"
    When I make a transfer from pesel: "40100912345" to pesel: "42061812876" with amount: "200.0"
    Then Account with pesel "40100912345" has "balance" equal to "800.0"
    And Account with pesel "42061812876" has "balance" equal to "200.0"

  Scenario: User is able to make an express transfer with fee
    Given Account registry is empty
    And I create an account using name: "freddie", last name: "mercury", pesel: "46090512987"
    And I create an account using name: "brian", last name: "may", pesel: "47071912654"
    And Account with pesel "46090512987" has balance of "500.0"
    When I make an express transfer from pesel: "46090512987" to pesel: "47071912654" with amount: "100.0"
    Then Account with pesel "46090512987" has "balance" equal to "399.0"
    And Account with pesel "47071912654" has "balance" equal to "100.0"

  Scenario: Transfer fails when sender has insufficient funds
    Given Account registry is empty
    And I create an account using name: "david", last name: "bowie", pesel: "47010812345"
    And I create an account using name: "iggy", last name: "pop", pesel: "47042112876"
    And Account with pesel "47010812345" has balance of "50.0"
    When I attempt a transfer from pesel: "47010812345" to pesel: "47042112876" with amount: "100.0"
    Then Transfer fails with error

  Scenario: User can receive multiple transfers
    Given Account registry is empty
    And I create an account using name: "mick", last name: "jagger", pesel: "43072612543"
    And I create an account using name: "keith", last name: "richards", pesel: "43121812765"
    And I create an account using name: "charlie", last name: "watts", pesel: "41060212987"
    And Account with pesel "43072612543" has balance of "1000.0"
    And Account with pesel "43121812765" has balance of "1000.0"
    When I make a transfer from pesel: "43072612543" to pesel: "41060212987" with amount: "150.0"
    And I make a transfer from pesel: "43121812765" to pesel: "41060212987" with amount: "250.0"
    Then Account with pesel "41060212987" has "balance" equal to "400.0"
    And Account with pesel "43072612543" has "balance" equal to "850.0"
    And Account with pesel "43121812765" has "balance" equal to "750.0"
