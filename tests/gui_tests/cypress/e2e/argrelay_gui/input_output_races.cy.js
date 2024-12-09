/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')
    })

    it('user moves cursor while pending response', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        const input_command_1 = 'lay goto host dev '
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(input_command_1)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_response_input')
        cy
            .get('[data-cy=command_line_input]')
            .type('{leftArrow}')
        // The bug was that `client_synced` state was never reached.
        // Conditions:
        // *   delay=500
        // *   no cache
        // *   TD_38_03_48_51 large generated data set
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
    })

    it('user modifies command line while pending request', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        // Use different input command from `input_command_1` (in previous test)
        // otherwise, response is too quick and `io_state_pending_request_input` is not reached:
        const input_command_2 = 'lay goto host '
        const extra_arg = 'qwer'
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(input_command_2)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_request_input')
        cy
            .get('[data-cy=command_line_input]')
            .type(extra_arg)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_request_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_response_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=suggestion_output]')
            .children()
            .should('have.length', 4)
    })

    it('user modifies command line while pending response', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        const input_command_3 = 'lay meta '
        const input_command_4 = 'lay '
        const extra_arg = 'qwer'
        // Type command which has suggestion:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(input_command_3)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_request_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_response_input')
        // Append extra arg which have no suggestions:
        cy
            .get('[data-cy=command_line_input]')
            .type(extra_arg)
        // No suggestions:
        cy
            .get('[data-cy=suggestion_output]')
            .children()
            .should('have.length', 0)
        // Wait for stability:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        // Still no suggestions:
        cy
            .get('[data-cy=suggestion_output]')
            .children()
            .should('have.length', 0)
        // Type command which has suggestion:
        cy
            .get('[data-cy=command_line_input]')
            .clear()
            .type(input_command_4)
        // Wait for stability:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=suggestion_output]')
            .children()
            .should('have.length', 13)
            .then(suggested_elems => {
                const suggested_strings = [...suggested_elems]
                    .map(suggested_elem => suggested_elem.textContent)
                expect(suggested_strings).to.have.length(13)
                expect(suggested_strings).to.include('desc')
                expect(suggested_strings).to.include('data')
                expect(suggested_strings).to.include('duplicates')
                expect(suggested_strings).to.include('config')
                expect(suggested_strings).to.include('diff')
                expect(suggested_strings).to.include('echo')
                expect(suggested_strings).to.include('enum')
                expect(suggested_strings).to.include('goto')
                expect(suggested_strings).to.include('help')
                expect(suggested_strings).to.include('intercept')
                expect(suggested_strings).to.include('list')
                expect(suggested_strings).to.include('no_data')
                expect(suggested_strings).to.include('ssh')
            })
    })
})
