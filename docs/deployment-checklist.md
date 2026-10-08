# Render Deployment Checklist

1. Push the repository to GitHub.
2. In Render, create a Blueprint from `render.yaml`.
3. Create the managed PostgreSQL database in the same region as the API service.
4. Set PayPal Sandbox secrets on the API service:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `PAYPAL_WEBHOOK_ID`
5. Set `DEMO_MODE=false` for a real PayPal Sandbox flow.
6. Update `CORS_ORIGINS` to the exact frontend `onrender.com` URL.
7. Update `VITE_API_BASE_URL` to the exact backend URL + `/api` and redeploy the frontend.
8. Configure the PayPal webhook listener URL as:
   `https://<backend-host>/api/paypal/webhook`
9. Test `/api/health` and `/api/ready`.
10. Test the budget-block and verification-fail scenarios before recording the demo.
