import { PayPalButtons } from '@paypal/react-paypal-js';

type PayPalButtonProps = {
  taskId: number;
  onSuccess: () => void;
};

export function PayPalButton({ taskId, onSuccess }: PayPalButtonProps) {
  return (
    <PayPalButtons
      style={{ layout: 'vertical', shape: 'rect', label: 'paypal' }}
      createOrder={async () => {
        const res = await fetch('http://127.0.0.1:8000/api/payments/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task_id: taskId }),
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        if (!data.paypal_order_id) throw new Error('PayPal order ID not returned');
        return data.paypal_order_id;
      }}
      onApprove={async () => { onSuccess(); }}
      onError={(err) => { console.error('PayPal checkout error:', err); }}
    />
  );
}
