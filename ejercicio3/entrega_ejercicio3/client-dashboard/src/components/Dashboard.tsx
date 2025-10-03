import React, { useState } from "react";
// FIX: Se eliminan las extensiones de archivo para resolver el módulo
import { useSalesData } from "../hooks/useSalesData";
// Importar el hook useFilters
// FIX: Se eliminan las extensiones de archivo para resolver el módulo
import { useFilters } from "../hooks/useFilters";
import type { SalesFilters, SalesMetrics } from "../types/types";
// FIX: Se elimina la extensión de archivo para resolver el módulo
import SalesChart from "./SalesChart";

const Dashboard: React.FC = () => {
  // 1. Uso del hook useSalesData
  const {
    cleanedData,
    metrics, // Métricas de los datos sin filtrar (para comparación o referencia)
    dailySales, // Ventas diarias de los datos sin filtrar
    products, // Lista de productos únicos
    loading,
    error,
    rawData,
  } = useSalesData();

  // 2. CAMBIO CLAVE: Usar useFilters en lugar de useState local
  const { filters, setDateRangeStart, setDateRangeEnd, setSelectedProduct, clearFilters, hasActiveFilters } = useFilters();

  // 3. Aplicar filtros a los datos limpios (mismo useMemo, ahora usando `filters` del hook)
  const filteredData = React.useMemo(() => {
    let data = [...cleanedData];

    // Filtro por rango de fechas
    if (filters.dateRange.start) {
      // Comparación de fecha de inicio (debe ser mayor o igual al inicio del día)
      // Se utiliza getTime() para comparación numérica de fechas
      const startOfDay = filters.dateRange.start.getTime();
      data = data.filter(
        (sale) => new Date(sale.date).getTime() >= startOfDay
      );
    }

    if (filters.dateRange.end) {
      // CORRECCIÓN CLAVE para asegurar la inclusión del día final: 
      // 1. Clonar la fecha de fin.
      const endOfDay = new Date(filters.dateRange.end);
      // 2. Establecer la hora al final del día (23:59:59.999) para incluir todas las ventas de ese día.
      endOfDay.setHours(23, 59, 59, 999); 
      // 3. Comparar el timestamp de la venta contra el timestamp de 'endOfDay'.
      const endOfDayTimestamp = endOfDay.getTime();
      
      data = data.filter(
        (sale) => new Date(sale.date).getTime() <= endOfDayTimestamp
      );
    }

    // Filtro por producto
    if (filters.selectedProduct) {
      data = data.filter((sale) => sale.product === filters.selectedProduct);
    }

    return data;
  }, [cleanedData, filters]);

  // 4. Calcular métricas para datos filtrados (mismo useMemo)
  const filteredMetrics = React.useMemo<SalesMetrics>(() => {
    if (filteredData.length === 0) {
      return {
        totalSales: 0,
        bestSellingProduct: null,
        averageRating: 0,
      };
    }

    const totalSales = filteredData.reduce(
      (sum, sale) => sum + sale.price * sale.quantity,
      0
    );

    const productQuantities: Record<string, number> = filteredData.reduce(
      (acc, sale) => {
        if (sale.product) {
          acc[sale.product] = (acc[sale.product] || 0) + sale.quantity;
        }
        return acc;
      },
      {} as Record<string, number>
    );

    const bestSellingProduct = Object.entries(productQuantities).reduce(
      (best, [product, quantity]) => {
        return quantity > (best.quantity || 0)
          ? { product, quantity }
          : best;
      },
      { product: null as string | null, quantity: 0 }
    ).product;

    const averageRating = filteredData.reduce(
      (sum, sale) => sum + sale.rating,
      0
    ) / filteredData.length;

    return {
      totalSales,
      bestSellingProduct,
      averageRating,
    };
  }, [filteredData]);

  // Manejo de estados de carga y error
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50">
        <p className="text-xl font-semibold text-gray-700">Cargando datos de ventas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-screen bg-red-50 p-6 rounded-lg shadow-lg">
        <p className="text-xl font-bold text-red-700">Error al cargar el Dashboard</p>
        <p className="text-gray-600 mt-2">Detalle: {error}</p>
      </div>
    );
  }

  // Componente de Botón de Filtro
  const FilterButton: React.FC<{ label: string; onClick: () => void; isSelected: boolean }> = ({ label, onClick, isSelected }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-full text-sm font-medium transition duration-150 ease-in-out ${
        isSelected
          ? "bg-blue-600 text-white shadow-md hover:bg-blue-700"
          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
      }`}
    >
      {label}
    </button>
  );

  // Componente de Entrada de Fecha
  const DateInput: React.FC<{ label: string; value: Date | null; onChange: (date: Date | null) => void }> = ({ label, value, onChange }) => (
    <div className="flex flex-col">
      <label className="text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type="date"
        value={value ? value.toISOString().split('T')[0] : ''}
        onChange={(e) => onChange(e.target.value ? new Date(e.target.value) : null)}
        className="px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      />
    </div>
  );

  return (
    <div className="p-6 md:p-10 bg-gray-50 min-h-screen font-sans">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-8 border-b pb-4">
        Dashboard de Ventas
      </h1>

      {/* Área de Filtros */}
      <div className="bg-white p-6 rounded-xl shadow-xl mb-8 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Control de Filtros</h2>
        
        <div className="flex flex-wrap items-end gap-4">
          {/* Filtros de Rango de Fechas */}
          <DateInput 
            label="Fecha Inicio" 
            value={filters.dateRange.start} 
            onChange={setDateRangeStart} 
          />
          <DateInput 
            label="Fecha Fin" 
            value={filters.dateRange.end} 
            onChange={setDateRangeEnd} 
          />

          {/* Selector de Producto */}
          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-700 mb-1">Producto</label>
            <select
              value={filters.selectedProduct || ''}
              onChange={(e) => setSelectedProduct(e.target.value || null)}
              className="px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 min-w-[150px]"
            >
              <option value="">Todos los Productos</option>
              {products.map((product) => (
                <option key={product} value={product}>
                  {product}
                </option>
              ))}
            </select>
          </div>

          {/* Botón de Limpiar Filtros */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-red-500 text-white rounded-lg shadow-md hover:bg-red-600 transition duration-150 ease-in-out font-medium mt-auto"
            >
              Limpiar Filtros
            </button>
          )}
        </div>
      </div>


      {/* Resumen de Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Tarjeta de Ventas Totales */}
        <div className="bg-white p-6 rounded-xl shadow-xl border-l-4 border-blue-500">
          <p className="text-sm font-medium text-gray-500">Ventas Totales (Filtradas)</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            ${filteredMetrics.totalSales.toFixed(2)}
          </p>
        </div>

        {/* Tarjeta de Producto Más Vendido */}
        <div className="bg-white p-6 rounded-xl shadow-xl border-l-4 border-green-500">
          <p className="text-sm font-medium text-gray-500">Producto Estrella (Filtrado)</p>
          <p className="text-2xl font-bold text-gray-900 mt-1 truncate">
            {filteredMetrics.bestSellingProduct || "-"}
          </p>
        </div>

        {/* Tarjeta de Calificación Promedio */}
        <div className="bg-white p-6 rounded-xl shadow-xl border-l-4 border-yellow-500">
          <p className="text-sm font-medium text-gray-500">Calificación Promedio</p>
          <div className="flex items-baseline">
            <p className="text-2xl font-bold text-gray-900">
              {filteredMetrics.averageRating.toFixed(1)}
            </p>
            <p className="text-sm text-gray-500 ml-2">/ 5.0</p>
          </div>
          <div className="flex mt-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <svg
                key={star}
                className={`h-4 w-4 ${
                  star <= Math.round(filteredMetrics.averageRating)
                    ? "text-yellow-400"
                    : "text-gray-300"
                }`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
          </div>
        </div>
      </div>

      {/* Gráfico de Ventas */}
      <SalesChart filteredData={filteredData} />
      
      {/* Sección Opcional: Métricas Generales (Sin Filtro) */}
      <div className="mt-8 pt-6 border-t border-gray-200">
         <h2 className="text-2xl font-bold text-gray-800 mb-4">Métricas Generales (Todos los Datos)</h2>
         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-100 p-4 rounded-xl shadow-inner">
               <p className="text-sm font-medium text-gray-500">Ventas Totales (Raw)</p>
               <p className="text-xl font-semibold text-gray-800 mt-1">${metrics.totalSales.toFixed(2)}</p>
            </div>
            <div className="bg-gray-100 p-4 rounded-xl shadow-inner">
               <p className="text-sm font-medium text-gray-500">Registros Totales</p>
               <p className="text-xl font-semibold text-gray-800 mt-1">{cleanedData.length}</p>
            </div>
            <div className="bg-gray-100 p-4 rounded-xl shadow-inner">
               <p className="text-sm font-medium text-gray-500">Productos Únicos</p>
               <p className="text-xl font-semibold text-gray-800 mt-1">{products.length}</p>
            </div>
         </div>
      </div>

    </div>
  );
};

export default Dashboard;
