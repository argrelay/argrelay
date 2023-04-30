/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')
    })

    it('server failure on first input but subsequent input succeeds', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        const input_command = 'relay_demo goto host dev '
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        // Simulate failure:
        cy
            .intercept('**', {forceNetworkError: true})
            .as('failed')
        // User types in command line:
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(input_command)
        // Wait for failure:
        cy
            .wait('@failed')
            .should('have.property', 'error')
        // Command line is in failed state:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_request_failed_input')
        // The failed state persists:
        cy
            .wait(5_000)
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_request_failed_input')
        // Remove failure simulation:
        cy
            .intercept('**', (req) => {
                req.continue()
            })
        // Modifies command line
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .type('{end}')
            .type(' ')
        // Everything works again:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_request_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_response_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
    })
})
