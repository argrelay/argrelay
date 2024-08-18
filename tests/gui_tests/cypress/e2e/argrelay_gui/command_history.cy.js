/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')
    })

    it('entered command is saved into history', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {
        const input_command = 'lay goto host'
        const extra_arg = 'qwer'
        cy
            .get('[data-cy=command_history]')
            .should('not.have.value', input_command)
        cy
            .get('[data-cy=command_history]')
            .children('option')
            .should('have.length', 0)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        // Enter 1st command:
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(`${input_command}{enter}`)
        cy
            .get('[data-cy=command_history]')
            .children('option')
            .then(all_options => {
                const text_lines = [...all_options]
                    .map(option_item => option_item.text)
                expect(text_lines).to.deep.eq([
                    `${input_command}`,
                ])
            })
        cy
            .get('[data-cy=command_history]')
            .children('option')
            .should('have.length', 1)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        // Enter 2nd command:
        cy
            .get('[data-cy=command_line_input]')
            .focus()
            .clear()
            .type(`${input_command} ${extra_arg}{enter}`)
        cy
            .get('[data-cy=command_history]')
            .children('option')
            .then(all_options => {
                const text_lines = [...all_options]
                    .map(option_item => option_item.text)
                expect(text_lines).to.deep.eq([
                    `${input_command} ${extra_arg}`,
                    `${input_command}`,
                ])
            })
        cy
            .get('[data-cy=command_history]')
            .children('option')
            .should('have.length', 2)
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
    })
})
