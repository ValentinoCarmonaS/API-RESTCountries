import React from 'react';
import type { DailySales, Sale } from '../types/types';
// Importaciones de Chart.js
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrar los componentes necesarios de Chart.js (Esencial para que funcione)
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Interfaz de propiedades actualizada: Solo necesitamos filteredData
interface SalesChartProps {
  filteredData: Sale[]; 
}

// El componente solo recibe los datos crudos filtrados (Sale[])
const SalesChart: React.FC<SalesChartProps> = ({ filteredData }) => {
  
  // Calcular datos del gráfico basados en los datos crudos filtrados
  // Esta lógica agrupa las ventas crudas por día.
  const chartData = React.useMemo(() => {
    // 1. Agrupar las ventas filtradas por fecha (solo el string de la fecha 'YYYY-MM-DD')
    const grouped = filteredData.reduce<Record<string, number>>(
      (acc, sale) => {
        // Asumimos que sale.date ya está en formato 'YYYY-MM-DD' por el preprocesamiento
        const date = sale.date; 
        if (!acc[date]) {
          acc[date] = 0;
        }
        acc[date] += sale.price * sale.quantity;
        return acc;
      },
      {}
    );

    // 2. Convertir el mapa a un array y ordenarlo por fecha
    return Object.entries(grouped)
      .map(([date, total]) => ({ date, total }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [filteredData]); // Dependencia del useMemo es solo filteredData

  if (chartData.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 text-center py-12">
        <p className="text-xl font-semibold text-gray-500">
          No hay datos de ventas para el rango de filtros seleccionado.
        </p>
      </div>
    );
  }
  
  // Preparar datos para Chart.js
  const labels = chartData.map(d => d.date);
  const dataValues = chartData.map(d => d.total);
  const maxValue = Math.max(...dataValues);

  const dataForChartJS = {
    labels,
    datasets: [
      {
        label: 'Ventas Diarias Totales',
        data: dataValues,
        borderColor: '#3b82f6', // blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.5)', 
        tension: 0.4, // Curvatura de la línea
        pointRadius: 4,
        pointBackgroundColor: '#1d4ed8', // blue-700
      },
    ],
  };

  // Opciones de configuración del gráfico
  const options = {
    responsive: true,
    maintainAspectRatio: false, // Permitir que el contenedor de altura fija funcione
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            family: 'Inter',
          }
        }
      },
      title: {
        display: true,
        text: 'Tendencia de Ventas Diarias (Filtrado)',
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            if (context.parsed.y !== null) {
                label += new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
        y: {
            title: {
                display: true,
                text: 'Ventas Totales ($)',
                font: { family: 'Inter', weight: 'bold' as const }
            },
            ticks: {
                callback: function(value: any) {
                    return '$' + value.toLocaleString();
                }
            }
        },
        x: {
            title: {
                display: true,
                text: 'Fecha',
                font: { family: 'Inter', weight: 'bold' as const }
            }
        }
    }
  };


  return (
    <div className="space-y-4">
      {/* Área del Gráfico de Ventas Diarias */}
      <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
        <div className="h-80"> {/* Altura fija para el gráfico */}
          <Line options={options} data={dataForChartJS} />
        </div>
      </div>

      {/* Resumen de datos, ahora debajo del gráfico */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
        <div>
          <p className="text-xs text-gray-500">Días con datos</p>
          <p className="text-lg font-semibold text-gray-900">{chartData.length}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Venta promedio/día</p>
          <p className="text-lg font-semibold text-gray-900">
            ${(chartData.reduce((sum, d) => sum + d.total, 0) / chartData.length).toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Mejor día (Ventas)</p>
          <p className="text-lg font-semibold text-gray-900">
            ${maxValue.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Peor día (Ventas)</p>
          <p className="text-lg font-semibold text-gray-900">
            ${Math.min(...dataValues).toFixed(2)}
          </p>
        </div>
      </div>

    </div>
  );
};

export default SalesChart;
