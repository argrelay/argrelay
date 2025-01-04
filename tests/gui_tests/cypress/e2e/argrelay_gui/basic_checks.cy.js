/// <reference types="cypress" />

describe('argrelay GUI', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8787/argrelay_gui/')

        cy
            .get('[data-cy=command_line_input]')
            .should('have.value', 'lay goto ')
    })

    it('has command line input ready', () => {
        cy
            .get('[data-cy=command_line_input]')
            .should('have.class', 'io_state_client_synced_input')
        cy
            .get('#command_line_input')
            .invoke('val')
            .should('have.length', 9)
        cy
            .get('#command_line_input')
            .invoke('val')
            .then((input_value) => {
                expect(input_value).to.be.equal('lay goto ')
            })
    })
})
