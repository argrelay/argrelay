
# Install Cypress

https://docs.cypress.io/guides/getting-started/installing-cypress

```sh
cd argrelay.git/tests/gui_tests
npm install cypress --save-dev
```

# Open Cypress / Initially

https://docs.cypress.io/guides/getting-started/opening-the-app

```sh
npx cypress open
```

*   Select E2E.
*   Select Chrome.
*   Press "Scaffold example specs".

# Open Cypress / Subsequently

See `argrelay_gui` dir.

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

# Run Cypress tests automatically

To pass tests successfully:
*   server has to be started (manually)
*   `TD_38_03_48_51` test data is required (which slows down responses due to its volume)

```sh
cd argrelay.git/tests/gui_tests
npx cypress run --spec cypress/e2e/argrelay_gui/**/*.cy.js
```
