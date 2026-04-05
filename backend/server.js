require('dotenv').config();
const express = require('express');
const cors    = require('cors');
const path    = require('path');
const db      = require('./db');

const app = express();
app.use(cors());
app.use(express.json());

// ── Static frontend ───────────────────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// ── API routes ────────────────────────────────────────────────────────────────
app.use('/api/auth',     require('./routes/auth'));
app.use('/api/user',     require('./routes/user'));
app.use('/api/bookings', require('./routes/bookings'));

// ── Fallback: serve index.html for any non-API route ─────────────────────────
app.get(/^(?!\/api\/).*/, (_req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

// ── Boot: initialise SQLite first, then start listening ───────────────────────
const PORT = process.env.PORT || 3001;

db.init()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`\n🚑  MediRush running at http://localhost:${PORT}\n`);
      if (!process.env.SMTP_HOST) {
        console.log('📧  SMTP not configured — OTPs will be printed to this console.\n');
      }
    });
  })
  .catch(err => {
    console.error('Failed to initialise database:', err);
    process.exit(1);
  });
