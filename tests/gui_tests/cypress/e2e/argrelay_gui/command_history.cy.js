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

    it('entered command is always inserted to head (even if matches existing history entry)', {
        // If cache is disabled and TD_38_03_48_51 large generated data set is used, it takes a while:
        defaultCommandTimeout: 30_000
    }, () => {

        // This should be synced with `argrelay_client.js` for the test to fill in entire history:
        const command_history_max_size = 10;
        // Loop more than `command_history_max_size`:
        const loop_count = command_history_max_size * 2;
        for (let command_index = 0; command_index < loop_count; command_index++) {
            // Enter different command initially then wrap to enter duplicates:
            const cycling_index = command_index % command_history_max_size
            const input_command = `lay goto host whatever_index${cycling_index}`
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
                    expect(text_lines[0]).eq(`${input_command}`)
                })
            cy
                .get('[data-cy=command_line_input]')
                .should('have.class', 'io_state_client_synced_input')
            }
    })
})
