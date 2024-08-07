/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')
    })

    it('suggestions get listed on command input', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        const input_command = 'relay_demo '
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(`${input_command}`)
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
            .should('have.length', 11)
            .then(suggested_elems => {
                const suggested_strings = [...suggested_elems]
                    .map(suggested_elem => suggested_elem.textContent)
                expect(suggested_strings).to.have.length(11)
                expect(suggested_strings).to.include('desc')
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
            })
    })
})
