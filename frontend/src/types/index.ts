export type Summary = {
  transactions: number;
  total_value: number;
  avg_risk: number;
  verification_rate: number;
  high_risk: number;
  blocked: number;
};

export type WorkflowResult = {
  task_id: number;
  status: string;
  selected_offer_id: number | null;
  selected_seller: string | null;
  negotiated_price: number | null;
  risk_score: number | null;
  risk_level: string | null;
  payment_status: string | null;
  verification_score: number | null;
  verification_status: string | null;
  message: string;
};

export type Transaction = {
  id: number;
  paypal_order_id: string | null;
  amount: number;
  currency: string;
  risk_score: number;
  verification_score: number;
  status: string;
  created_at: string;
};
