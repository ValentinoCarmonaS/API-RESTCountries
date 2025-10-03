import { describe, test, expect } from '@jest/globals';
import {
  findInvalidSales,
  fixSale,
  separateSales,
  combineSalesForExport
} from '../utils/qaUtils';
import { Sale, SaleError } from '../types';

describe('qaUtils', () => {
  describe('findInvalidSales', () => {
    test('should identify sales with null product', () => {
      const sales: Sale[] = [
        { id: 1, product: null, quantity: 1, price: 100, date: '2024-01-01' }
      ];

      const invalid = findInvalidSales(sales);

      expect(invalid).toHaveLength(1);
      expect(invalid[0].errors).toContain('Producto no válido: el campo producto está vacío o es nulo');
    });

    test('should identify sales with negative quantity', () => {
      const sales: Sale[] = [
        { id: 1, product: 'Test', quantity: -5, price: 100, date: '2024-01-01' }
      ];

      const invalid = findInvalidSales(sales);

      expect(invalid).toHaveLength(1);
      expect(invalid[0].errors).toContain('Cantidad negativa: -5');
    });

    test('should identify sales with zero quantity', () => {
      const sales: Sale[] = [
        { id: 1, product: 'Test', quantity: 0, price: 100, date: '2024-01-01' }
      ];

      const invalid = findInvalidSales(sales);

      expect(invalid).toHaveLength(1);
      expect(invalid[0].errors).toContain('Cantidad cero: no se puede vender 0 unidades');
    });

    test('should identify multiple errors in a single sale', () => {
      const sales: Sale[] = [
        { id: 1, product: null, quantity: -5, price: 100, date: '2024-01-01' }
      ];

      const invalid = findInvalidSales(sales);

      expect(invalid).toHaveLength(1);
      expect(invalid[0].errors).toHaveLength(2);
    });

    test('should return empty array for valid sales', () => {
      const sales: Sale[] = [
        { id: 1, product: 'Laptop', quantity: 2, price: 1000, date: '2024-01-01' }
      ];

      const invalid = findInvalidSales(sales);

      expect(invalid).toHaveLength(0);
    });
  });

  describe('fixSale', () => {
    test('should fix null product', () => {
      const saleError: SaleError = {
        sale: { id: 1, product: null, quantity: 1, price: 100, date: '2024-01-01' },
        errors: ['Producto no válido: el campo producto está vacío o es nulo']
      };

      const fixed = fixSale(saleError);

      expect(fixed.product).toBe('Producto Desconocido');
      expect(fixed.wasFixed).toBe(true);
    });

    test('should fix negative quantity', () => {
      const saleError: SaleError = {
        sale: { id: 1, product: 'Test', quantity: -5, price: 100, date: '2024-01-01' },
        errors: ['Cantidad negativa: -5']
      };

      const fixed = fixSale(saleError);

      expect(fixed.quantity).toBe(5);
      expect(fixed.wasFixed).toBe(true);
    });

    test('should fix zero quantity', () => {
      const saleError: SaleError = {
        sale: { id: 1, product: 'Test', quantity: 0, price: 100, date: '2024-01-01' },
        errors: ['Cantidad cero: no se puede vender 0 unidades']
      };

      const fixed = fixSale(saleError);

      expect(fixed.quantity).toBe(1);
      expect(fixed.wasFixed).toBe(true);
    });

    test('should preserve original errors', () => {
      const saleError: SaleError = {
        sale: { id: 1, product: null, quantity: -5, price: 100, date: '2024-01-01' },
        errors: ['Error 1', 'Error 2']
      };

      const fixed = fixSale(saleError);

      expect(fixed.originalErrors).toEqual(['Error 1', 'Error 2']);
    });
  });

  describe('separateSales', () => {
    test('should correctly separate valid and invalid sales', () => {
      const sales: Sale[] = [
        { id: 1, product: 'Valid', quantity: 1, price: 100, date: '2024-01-01' },
        { id: 2, product: null, quantity: 1, price: 100, date: '2024-01-01' },
        { id: 3, product: 'Valid2', quantity: 2, price: 200, date: '2024-01-01' }
      ];

      const { valid, invalid } = separateSales(sales);

      expect(valid).toHaveLength(2);
      expect(invalid).toHaveLength(1);
      expect(invalid[0].sale.id).toBe(2);
    });
  });

  describe('combineSalesForExport', () => {
    test('should combine valid and fixed sales', () => {
      const validSales: Sale[] = [
        { id: 1, product: 'Valid', quantity: 1, price: 100, date: '2024-01-01' }
      ];

      const fixedSales = [
        {
          id: 2,
          product: 'Fixed',
          quantity: 1,
          price: 100,
          date: '2024-01-01',
          wasFixed: true,
          originalErrors: ['Some error']
        }
      ];

      const combined = combineSalesForExport(validSales, fixedSales);

      expect(combined).toHaveLength(2);
      expect(combined[1]).not.toHaveProperty('wasFixed');
      expect(combined[1]).not.toHaveProperty('originalErrors');
    });
  });
});
