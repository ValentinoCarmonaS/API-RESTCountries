import { useState, useEffect, useMemo } from 'react';
import type { Sale, SalesMetrics, DailySales } from '../types/types';

export const useSalesData = () => {
  const [rawData, setRawData] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar datos del archivo JSON
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/sales_data.json');
        if (!response.ok) {
          throw new Error('Error al cargar los datos');
        }
        
        const jsonResponse: { sales: Sale[] } = await response.json();
        setRawData(jsonResponse.sales);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);


  // Limpiar datos corruptos
  const cleanedData = useMemo(() => {
    return rawData.filter(sale => {
      // Excluir registros con quantity < 0 o product === null
      return sale.quantity >= 0 && sale.product !== null;
    });
  }, [rawData]);

  // Calcular métricas
  const metrics = useMemo<SalesMetrics>(() => {
    if (cleanedData.length === 0) {
      return {
        totalSales: 0,
        bestSellingProduct: null,
        averageRating: 0
      };
    }

    // Ventas totales
    const totalSales = cleanedData.reduce(
      (sum, sale) => sum + (sale.price * sale.quantity),
      0
    );

    // Producto más vendido
    const productQuantities = cleanedData.reduce<Record<string, number>>(
      (acc, sale) => {
        if (sale.product) {
          acc[sale.product] = (acc[sale.product] || 0) + sale.quantity;
        }
        return acc;
      },
      {}
    );

    const bestSellingProduct = Object.entries(productQuantities).reduce(
      (best, [product, quantity]) => {
        return quantity > (best.quantity || 0)
          ? { product, quantity }
          : best;
      },
      { product: null as string | null, quantity: 0 }
    ).product;

    // Rating promedio
    const averageRating = cleanedData.reduce(
      (sum, sale) => sum + sale.rating,
      0
    ) / cleanedData.length;

    return {
      totalSales,
      bestSellingProduct,
      averageRating
    };
  }, [cleanedData]);

  // Agrupar ventas por día
  const dailySales = useMemo<DailySales[]>(() => {
    const grouped = cleanedData.reduce<Record<string, DailySales>>(
      (acc, sale) => {
        const date = sale.date;
        if (!acc[date]) {
          acc[date] = { date, total: 0, count: 0 };
        }
        acc[date].total += sale.price * sale.quantity;
        acc[date].count += 1;
        return acc;
      },
      {}
    );

    return Object.values(grouped).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [cleanedData]);

  // Obtener lista de productos únicos
  const products = useMemo(() => {
    const uniqueProducts = new Set(
      cleanedData
        .map(sale => sale.product)
        .filter((product): product is string => product !== null)
    );
    return Array.from(uniqueProducts).sort();
  }, [cleanedData]);

  return {
    rawData,
    cleanedData,
    metrics,
    dailySales,
    products,
    loading,
    error
  };
};
