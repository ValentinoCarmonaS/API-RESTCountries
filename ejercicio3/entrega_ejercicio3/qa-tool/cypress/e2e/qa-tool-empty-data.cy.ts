/// <reference types="cypress" />
describe('QA Tool - Datos Vacíos', () => {
  beforeEach(() => {
    cy.intercept('GET', '/sales_data.json', {
      statusCode: 200,
      body: { sales: [] }
    }).as('loadEmptyData');

    cy.visit('/');
    cy.wait('@loadEmptyData');
  });

  it('should display no data message', () => {
    cy.contains('No se encontraron errores en los datos de ventas.').should('be.visible');
  });

  it('should disable export button', () => {
    cy.get('button:contains("Exportar a JSON")').should('be.disabled');
  });
});