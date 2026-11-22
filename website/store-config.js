// PLAYTREE Store - Stripe Configuration
// ============================================================
// To enable real payments:
// 1. Create a Stripe account at https://stripe.com
// 2. Create Payment Links in your Stripe Dashboard for each product
// 3. Paste the Payment Link URLs below
// 4. Set your publishable key (pk_live_... or pk_test_...) in the meta tag below
//    or via environment variable STRIPE_PUBLISHABLE_KEY
// 5. NEVER put your secret key (sk_...) in frontend code - keep it server-side
// ============================================================

// Stripe publishable key (safe to expose in frontend)
// Set via: <meta name="stripe-pk" content="pk_live_...">
window.PLAYTREE_STRIPE_PK = (document.querySelector('meta[name="stripe-pk"]') || {}).content || '';

// Stripe Payment Links (create these in your Stripe Dashboard)
// Format: 'points_500': 'https://buy.stripe.com/...'
window.PLAYTREE_STRIPE_LINKS = {
  // Tree Points
  'points_500':   '',  // Starter Pack - 500 TP - $4.99
  'points_1300':  '',  // Value Pack - 1,300 TP - $9.99
  'points_3500':  '',  // Mega Pack - 3,500 TP - $24.99
  // Tree Coins
  'coins_1000':   '',  // Coin Pouch - 1,000 TC - $2.99
  'coins_3500':   '',  // Coin Chest - 3,500 TC - $7.99
  'coins_12000':  '',  // Coin Vault - 12,000 TC - $19.99
};

// Initialize Stripe.js if publishable key is set
if (window.PLAYTREE_STRIPE_PK && window.Stripe) {
  window.stripe = window.Stripe(window.PLAYTREE_STRIPE_PK);
}