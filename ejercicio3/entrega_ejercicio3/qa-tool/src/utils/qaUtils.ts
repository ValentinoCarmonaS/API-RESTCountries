import { Sale, SaleError, FixedSale } from '../types/index';

/**
 * Identifica ventas inválidas y devuelve los registros con sus errores
 */
export function findInvalidSales(sales: Sale[]): SaleError[] {
  const invalidSales: SaleError[] = [];

  sales.forEach((sale) => {
    const errors: string[] = [];

    // Verificar si el producto es null o vacío
    if (!sale.product || sale.product.trim() === '') {
      errors.push('Producto no válido: el campo producto está vacío o es nulo');
    }

    // Verificar si la cantidad es negativa
    if (sale.quantity < 0) {
      errors.push(`Cantidad negativa: ${sale.quantity}`);
    }

    // Verificar si la cantidad es cero (podría ser un error dependiendo del negocio)
    if (sale.quantity === 0) {
      errors.push('Cantidad cero: no se puede vender 0 unidades');
    }

    // Verificar si el precio es válido
    if (sale.price <= 0) {
      errors.push(`Precio inválido: ${sale.price}`);
    }

    // Si hay errores, agregar a la lista de ventas inválidas
    if (errors.length > 0) {
      invalidSales.push({
        sale,
        errors
      });
    }
  });

  return invalidSales;
}

/**
 * Corrige una venta inválida según reglas de negocio predefinidas
 */
export function fixSale(saleError: SaleError): FixedSale {
  const fixedSale: FixedSale = { ...saleError.sale };
  const originalErrors = [...saleError.errors];

  // Corregir producto nulo o vacío
  if (!fixedSale.product || fixedSale.product.trim() === '') {
    fixedSale.product = 'Producto Desconocido';
  }

  // Corregir cantidad negativa (convertir a positivo)
  if (fixedSale.quantity < 0) {
    fixedSale.quantity = Math.abs(fixedSale.quantity);
  }

  // Corregir cantidad cero (establecer a 1 como mínimo)
  if (fixedSale.quantity === 0) {
    fixedSale.quantity = 1;
  }

  // Corregir precio inválido (establecer precio mínimo)
  if (fixedSale.price <= 0) {
    fixedSale.price = 0.01;
  }

  // Marcar como corregido y guardar errores originales
  fixedSale.wasFixed = true;
  fixedSale.originalErrors = originalErrors;

  return fixedSale;
}

/**
 * Separa las ventas en válidas e inválidas
 */
export function separateSales(sales: Sale[]): {
  valid: Sale[];
  invalid: SaleError[];
} {
  const invalid = findInvalidSales(sales);
  const invalidIds = new Set(invalid.map(item => item.sale.id));
  const valid = sales.filter(sale => !invalidIds.has(sale.id));

  return { valid, invalid };
}

/**
 * Combina ventas válidas y corregidas para exportación
 */
export function combineSalesForExport(
  validSales: Sale[],
  fixedSales: FixedSale[]
): Sale[] {
  // Limpiar los campos adicionales de las ventas corregidas
  const cleanedFixedSales = fixedSales.map(({ wasFixed, originalErrors, ...sale }) => sale);

  return [...validSales, ...cleanedFixedSales];
}

/**
 * Genera un archivo JSON para descarga
 */
export function downloadJSON(data: any, filename: string = 'sales_data_cleaned.json'): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}
