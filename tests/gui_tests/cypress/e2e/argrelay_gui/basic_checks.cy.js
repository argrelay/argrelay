/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')
    })

    it('has command line input ready', () => {
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('#command_line_input')
            .should('have.length', 1)
        cy
            .get('#command_line_input')
            .first()
            .should('have.text', '')
    })
})
