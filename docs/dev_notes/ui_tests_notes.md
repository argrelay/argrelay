
# Install Cypress

https://docs.cypress.io/guides/getting-started/installing-cypress

```sh
cd argrelay.git/tests/ui_tests
npm install cypress --save-dev
```

# Open Cypress

https://docs.cypress.io/guides/getting-started/opening-the-app

```sh
npx cypress open
```

*   Select E2E.
*   Select Chrome.
*   Press "Scaffold example specs".
*   Try running `basic_checks.cy.js`.

In case of this error:

```
Error: error:0308010C:digital envelope routines::unsupported
```

follow this answer:

https://stackoverflow.com/a/69699772/441652

```sh
export NODE_OPTIONS=--openssl-legacy-provider
```

# Fist Cypress test

See `argrelay_gui`.

# Run Cypress tests

```sh
cd argrelay.git/tests/ui_tests
npx cypress run --spec cypress/e2e/argrelay_gui/**/*.cy.js
```
