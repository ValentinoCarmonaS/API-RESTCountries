// cypress/e2e/qa-tool-valid-data.cy.ts
/// <reference types="cypress" />
describe('QA Tool - Datos Válidos', () => {
  beforeEach(() => {
    // Mock de datos válidos
    cy.intercept('GET', '/sales_data.json', {
      statusCode: 200,
      body: {
        sales: [
          { id: 1, product: 'Laptop', quantity: 2, price: 1200, date: '2024-01-15', rating: 5 },
          { id: 2, product: 'Mouse', quantity: 5, price: 25, date: '2024-01-16', rating: 4 },
          { id: 3, product: 'Keyboard', quantity: 3, price: 75, date: '2024-01-17', rating: 5 }
        ]
      }
    }).as('loadValidData');

    cy.visit('/');
    cy.wait('@loadValidData');
  });

  it('should display success message when no errors found', () => {
    cy.contains('No se encontraron errores en los datos de ventas.').should('be.visible');
  });

  it('should show correct statistics for valid data', () => {
   it('should show correct statistics for valid data', () => {
    cy.contains('div', 'Total de Registros').should('contain.text', '3');
    cy.contains('div', 'Registros con Errores').should('contain.text', '0');
    cy.contains('div', 'Registros Válidos').should('contain.text', '3');
  });
  });

  it('should enable export button for valid data', () => {
    cy.get('button:contains("Exportar a JSON")').should('be.enabled');
  });

  it('should not show errors table', () => {
    cy.get('table').should('not.exist');
    cy.contains('Registros con Errores').should('be.visible');
    cy.get('button:contains("Corregir")').should('not.exist');
  });
});