const router = require('express').Router();
const db     = require('../db');
const auth   = require('../middleware/auth');

// ── GET /api/bookings ─────────────────────────────────────────────────────────
router.get('/', auth, (req, res) => {
  try {
    const bookings = db
      .prepare('SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC')
      .all(req.user.id);
    res.json(bookings);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ── POST /api/bookings ────────────────────────────────────────────────────────
router.post('/', auth, (req, res) => {
  try {
    const {
      patient_name, patient_phone, location,
      emergency_type, ambulance_type,
      severity_level, severity_word,
      description, eta_minutes, unit_assigned,
    } = req.body;

    if (!location || !emergency_type || !severity_level)
      return res.status(400).json({ error: 'location, emergency_type, and severity_level are required.' });

    const request_id = 'MR-' + Date.now().toString().slice(-6);

    db.prepare(`
      INSERT INTO bookings
        (user_id, request_id, patient_name, patient_phone, location,
         emergency_type, ambulance_type, severity_level, severity_word,
         description, eta_minutes, unit_assigned)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      req.user.id, request_id,
      patient_name  || null, patient_phone || null, location,
      emergency_type, ambulance_type || null,
      severity_level, severity_word || null,
      description || null, eta_minutes || null, unit_assigned || null,
    );

    res.status(201).json({ request_id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

module.exports = router;
