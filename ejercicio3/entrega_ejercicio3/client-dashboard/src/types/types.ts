// Interfaz para un registro de venta
export interface Sale {
  id: number;
  product: string | null;
  price: number;
  quantity: number;
  date: string;
  rating: number;
}

// Interfaz para las métricas calculadas
export interface SalesMetrics {
  totalSales: number;
  bestSellingProduct: string | null;
  averageRating: number;
}

// Interfaz para los filtros
export interface SalesFilters {
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  selectedProduct: string | null;
}

// Interfaz para los datos agrupados por día
export interface DailySales {
  date: string;
  total: number;
  count: number;
}