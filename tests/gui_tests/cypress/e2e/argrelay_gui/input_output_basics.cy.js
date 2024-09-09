/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')

        cy
            .get('[data-cy=command_line_input]')
            .should('have.value', 'lay ')
    })

    it('suggestions get listed on command input', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {

        // Use `some_command` instead of `lay` (because `lay` is default and LRU-cached with quick response):
        const input_command = 'some_command '

        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(`${input_command}`)

        // A series of state transitions while talking to server:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_request_input')
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_pending_response_input')
        // Final (stable) output:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')

        cy
            .get('[data-cy=suggestion_output]')
            .children()
            .should('have.length', 12)
            .then(suggested_elems => {
                const suggested_strings = [...suggested_elems]
                    .map(suggested_elem => suggested_elem.textContent)
                expect(suggested_strings).to.have.length(12)
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
                expect(suggested_strings).to.include('meta')
                expect(suggested_strings).to.include('no_data')
            })
    })

    it('suggestions get listed on command input', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {

        // This test will select (out of order) the following line by clicking remaining items:
        const input_command_first_arg = 'lay'
        const input_command_args = [
            'func_id_list_service',
            'duplicates',
            'active',
            'sss',
        ]
        const input_command_last_arg = 'dc.44'

        // Initial (stable) output:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // first arg

        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(`${input_command_first_arg} `)
        // Final (stable) output:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        // Has suggestions:
            cy
                .get('[data-cy=suggestion_output]')
                .get('.suggested_item')
                .then(suggested_elems => {
                    expect(suggested_elems).to.have.length.greaterThan(0)
                });

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // mid args

        for (const input_arg of input_command_args) {
            cy
                .get('[data-cy=remaining_output]')
                .get('.remaining_item')
                .contains(input_arg)
                .click()
            // Final (stable) output:
            cy
                .get('[data-cy=command_line_input]')
                .should('have.class', 'io_state_client_synced_input')
            // Has suggestions:
            cy
                .get('[data-cy=suggestion_output]')
                .get('.suggested_item')
                .then(suggested_elems => {
                    expect(suggested_elems).to.have.length.greaterThan(0)
                });
        }

        ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // last arg
        cy
            .get('[data-cy=remaining_output]')
            .get('.remaining_item')
            .contains(input_command_last_arg)
            .click()
        // Final (stable) output:
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')

        // Has no more suggestions:
        cy
            .get('[data-cy=suggestion_output]')
            .get('.suggested_item')
            .should('have.length', 0)
    })
})
