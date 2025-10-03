import React from 'react';
import { SaleError, FixedSale } from '../types/index';

interface ErrorsTableProps {
  errors: SaleError[];
  fixedSales: FixedSale[];
  onFix: (saleError: SaleError) => void;
}

const ErrorsTable: React.FC<ErrorsTableProps> = ({ errors, fixedSales, onFix }) => {
  const isFixed = (saleId: number) => {
    return fixedSales.some(sale => sale.id === saleId);
  };

  if (errors.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No se encontraron errores en los datos de ventas.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto shadow-md rounded-lg">
      <table className="min-w-full bg-white">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Producto
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cantidad
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Precio
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Errores
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acción
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {errors.map((error) => {
            const fixed = isFixed(error.sale.id);
            return (
              <tr
                key={error.sale.id}
                className={fixed ? 'bg-green-50' : 'hover:bg-gray-50'}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {error.sale.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className={!error.sale.product ? 'text-red-600 font-semibold' : ''}>
                    {error.sale.product || 'NULL'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className={error.sale.quantity < 0 || error.sale.quantity === 0 ? 'text-red-600 font-semibold' : ''}>
                    {error.sale.quantity}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ${error.sale.price.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {error.sale.date}
                </td>
                <td className="px-6 py-4 text-sm text-red-600">
                  <ul className="list-disc list-inside">
                    {error.errors.map((err, index) => (
                      <li key={index} className="text-xs">
                        {err}
                      </li>
                    ))}
                  </ul>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {fixed ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Corregido
                    </span>
                  ) : (
                    <button
                      onClick={() => onFix(error)}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Corregir
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ErrorsTable;
