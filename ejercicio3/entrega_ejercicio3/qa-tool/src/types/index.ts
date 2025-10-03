export interface Sale {
  id: number;
  product: string | null;
  quantity: number;
  price: number;
  date: string;
}

export interface SaleError {
  sale: Sale;
  errors: string[];
}

export interface FixedSale extends Sale {
  wasFixed?: boolean;
  originalErrors?: string[];
}
