import React, { useState, useEffect } from "react";
import { Sale, SaleError, FixedSale } from "../types/index";
import {
  separateSales,
  fixSale,
  combineSalesForExport,
  downloadJSON,
} from "../utils/qaUtils";
import ErrorsTable from "./ErrorsTable";

const QATool: React.FC = () => {
  const [salesData, setSalesData] = useState<Sale[]>([]);
  const [validSales, setValidSales] = useState<Sale[]>([]);
  const [invalidSales, setInvalidSales] = useState<SaleError[]>([]);
  const [fixedSales, setFixedSales] = useState<FixedSale[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSalesData();
  }, []);

  const loadSalesData = async () => {
    try {
      setLoading(true);
      let data: { sales: Sale[] };

      const response = await fetch("/sales_data.json");

      if (!response.ok) {
        const second_response = await fetch(
          "../../../client-dashboard/public/sales_data.json"
        );

        if (!second_response.ok) {
          throw new Error("No se pudo cargar el archivo sales_data.json");
        } else data = await second_response.json();
      } else data = await response.json();

      processSalesData(data.sales);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar datos");
    } finally {
      setLoading(false);
    }
  };

  const useExampleData = () => {
    const exampleData: Sale[] = [
      {
        id: 1,
        product: "Laptop",
        quantity: 2,
        price: 1200,
        date: "2024-01-15",
      },
      { id: 2, product: null, quantity: 1, price: 800, date: "2024-01-16" },
      { id: 3, product: "Mouse", quantity: -5, price: 25, date: "2024-01-17" },
      {
        id: 4,
        product: "Keyboard",
        quantity: 3,
        price: 75,
        date: "2024-01-18",
      },
      { id: 5, product: null, quantity: -2, price: 150, date: "2024-01-19" },
      {
        id: 6,
        product: "Monitor",
        quantity: 1,
        price: 350,
        date: "2024-01-20",
      },
      { id: 7, product: "Webcam", quantity: 0, price: 120, date: "2024-01-21" },
      { id: 8, product: "", quantity: 2, price: 200, date: "2024-01-22" },
      {
        id: 9,
        product: "Headphones",
        quantity: 4,
        price: 89.99,
        date: "2024-01-23",
      },
      {
        id: 10,
        product: "USB Cable",
        quantity: -10,
        price: 15,
        date: "2024-01-24",
      },
    ];
    processSalesData(exampleData);
    setError(
      "Usando datos de ejemplo. Para usar datos reales, asegúrese de que el archivo sales_data.json esté disponible."
    );
  };

  const processSalesData = (data: Sale[]) => {
    setSalesData(data);
    const { valid, invalid } = separateSales(data);
    setValidSales(valid);
    setInvalidSales(invalid);
  };

  const handleFixSale = (saleError: SaleError) => {
    const fixed = fixSale(saleError);
    setFixedSales((prev) => [...prev, fixed]);
  };

  const handleExport = () => {
    const exportData = combineSalesForExport(validSales, fixedSales);
    downloadJSON(exportData, "sales_data_cleaned.json");
  };

  const totalRecords = salesData.length;
  const validCount = validSales.length;
  const invalidCount = invalidSales.length;
  const fixedCount = fixedSales.length;
  const remainingErrors = invalidCount - fixedCount;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Herramienta de QA - Limpieza de Datos de Ventas
        </h1>
        <p className="text-gray-600">
          Identifica, corrige y exporta datos de ventas limpios
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-yellow-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">
            Total de Registros
          </div>
          <div className="mt-2 text-3xl font-bold text-gray-900">
            {totalRecords}
          </div>
        </div>

        <div className="bg-green-50 shadow rounded-lg p-6">
          <div className="text-sm font-medium text-green-700">
            Registros Válidos
          </div>
          <div className="mt-2 text-3xl font-bold text-green-900">
            {validCount}
          </div>
        </div>

        <div className="bg-red-50 shadow rounded-lg p-6">
          <div className="text-sm font-medium text-red-700">
            Registros con Errores
          </div>
          <div className="mt-2 text-3xl font-bold text-red-900">
            {invalidCount}
          </div>
        </div>

        <div className="bg-blue-50 shadow rounded-lg p-6">
          <div className="text-sm font-medium text-blue-700">
            Registros Corregidos
          </div>
          <div className="mt-2 text-3xl font-bold text-blue-900">
            {fixedCount}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {invalidCount > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Progreso de Corrección
            </span>
            <span className="text-sm font-medium text-gray-700">
              {fixedCount} de {invalidCount} corregidos
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${(fixedCount / invalidCount) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Errors Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Registros con Errores
          </h2>
          {remainingErrors === 0 && invalidCount > 0 && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              ✓ Todos los errores han sido corregidos
            </span>
          )}
        </div>
        <ErrorsTable
          errors={invalidSales}
          fixedSales={fixedSales}
          onFix={handleFixSale}
        />
      </div>

      {/* Export Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Exportar Datos Limpios
            </h3>
            <p className="mt-1 text-sm text-gray-600">
              Incluye {validCount} registros válidos originales + {fixedCount}{" "}
              registros corregidos
            </p>
          </div>
          <button
            onClick={handleExport}
            disabled={totalRecords === 0}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
              totalRecords === 0
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            }`}
          >
            <svg
              className="mr-2 h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Exportar a JSON
          </button>
        </div>
      </div>
    </div>
  );
};

export default QATool;
