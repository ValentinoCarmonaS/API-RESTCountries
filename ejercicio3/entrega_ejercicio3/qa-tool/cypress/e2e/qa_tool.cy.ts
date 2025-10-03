/// <reference types="cypress" />
describe("QA Tool E2E Tests", () => {
  beforeEach(() => {
    // Mock de datos válidos
    cy.intercept("GET", "/sales_data.json", {
      statusCode: 200,
      body: {
        sales: [
          {
            id: 1,
            date: "2023-01-15",
            product: "Laptop",
            quantity: 2,
            price: 1200,
            rating: 4.5,
          },
          {
            id: 2,
            date: "2023-01-15",
            product: "Mouse",
            quantity: -3,
            price: 25,
            rating: 3.8,
          },
          {
            id: 3,
            date: "2023-01-16",
            product: null,
            quantity: 1,
            price: 300,
            rating: 5.0,
          },
        ],
      },
    }).as("loadValidData");

    cy.visit("/");
    cy.wait("@loadValidData");
  });

  it("should load sales data and display a table", () => {
    // Verifica que la tabla se renderice y contenga al menos una fila de datos
    cy.get("table").should("be.visible");
    cy.get("tbody tr").should("have.length.greaterThan", 0);
  });

  it("should identify an error for null product and allow correction", () => {
    // 0. La tabla "Registros con Errores" debe existir y ser visible
    cy.get('div:contains("Registros con Errores")').should('be.visible');

    // 1. Encuentra la fila que contiene el mensaje de error "Producto nulo o vacío"
    cy.contains(
      "tr",
      "Producto no válido: el campo producto está vacío o es nulo"
    ).as("errorRow");

    // 2. Verifica que la fila encontrada contenga el botón "Corregir"
    cy.get("@errorRow").within(() => {
      cy.get("button").contains("Corregir").should("be.visible");
    });

    // 3. Haz clic en el botón "Corregir"
    cy.get("@errorRow").find("button").contains("Corregir").click();

    // 4. Verifica que el boton ya no se pueda hacer click.
    cy.get("@errorRow").find('button:contains("Corregir")').should('not.exist');  
  });

  it("should identify an error for negative quantity and allow correction", () => {
    // 1. Encuentra la fila con el error de cantidad negativa
    cy.contains("tr", "Cantidad negativa").as("errorRow");

    // 2. Haz clic en el botón "Corregir"
    cy.get("@errorRow").find("button").contains("Corregir").click();

    // 3. Verifica que la cantidad se haya corregido a su valor absoluto (3)
    cy.get("@errorRow").contains("td", "3").should("be.visible");

      // Verifica que el botón "Corregir" ya no exista
    cy.get("@errorRow").find('button:contains("Corregir")').should('not.exist');

  });

  it("should correct all errors and exporting data", () => {
    // Verifica que el botón de exportar esté deshabilitado al principio
    cy.contains("button", "Exportar a JSON").should("be.enabled");

    cy.contains(
      "tr",
      "Producto no válido: el campo producto está vacío o es nulo"
    ).as("errorRow1");

    cy.get("@errorRow1").within(() => {
      cy.get("button").contains("Corregir").should("be.visible");
      cy.get("button").contains("Corregir").click();
      cy.get("@errorRow1").find('button:contains("Corregir")').should('not.exist');
    });

    cy.contains(
      "tr",
      "Cantidad negativa: -3"
    ).as("errorRow2");

    cy.get("@errorRow2").within(() => {
      cy.get("button").contains("Corregir").should("be.visible");
      cy.get("button").contains("Corregir").click();
      cy.get("@errorRow2").find('button:contains("Corregir")').should('not.exist');
    });

    // Verifica que el mensaje de "Todos los errores han sido corregidos" aparezca
    cy.contains("Todos los errores han sido corregidos").should("be.visible");

    // Verifica que el botón de exportar ahora esté habilitado
    cy.contains("button", "Exportar a JSON").should("be.enabled");

    // Opcional: Haz clic en exportar para asegurar que no falle
    cy.contains("button", "Exportar a JSON").click();
  });
});