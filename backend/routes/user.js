const router = require('express').Router();
const db     = require('../db');
const auth   = require('../middleware/auth');

// ── GET /api/user/profile ─────────────────────────────────────────────────────
router.get('/profile', auth, (req, res) => {
  try {
    const user = db.prepare(
      'SELECT id, email, full_name, phone, created_at FROM users WHERE id = ?'
    ).get(req.user.id);
    if (!user) return res.status(404).json({ error: 'User not found.' });

    const medical = db.prepare('SELECT * FROM user_medical WHERE user_id = ?').get(req.user.id);
    res.json({ ...user, medical: medical || {} });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ── PUT /api/user/profile ─────────────────────────────────────────────────────
router.put('/profile', auth, (req, res) => {
  try {
    const {
      full_name, phone,
      blood_type, allergies, medications, conditions,
      emergency_contact_name, emergency_contact_phone,
    } = req.body;

    db.prepare('UPDATE users SET full_name = ?, phone = ? WHERE id = ?')
      .run(full_name || null, phone || null, req.user.id);

    const hasMedical = db.prepare('SELECT user_id FROM user_medical WHERE user_id = ?').get(req.user.id);
    if (hasMedical) {
      db.prepare(`
        UPDATE user_medical
        SET blood_type=?, allergies=?, medications=?, conditions=?,
            emergency_contact_name=?, emergency_contact_phone=?
        WHERE user_id=?
      `).run(
        blood_type || null, allergies || null, medications || null, conditions || null,
        emergency_contact_name || null, emergency_contact_phone || null,
        req.user.id,
      );
    } else {
      db.prepare(`
        INSERT INTO user_medical
          (user_id, blood_type, allergies, medications, conditions,
           emergency_contact_name, emergency_contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(
        req.user.id,
        blood_type || null, allergies || null, medications || null, conditions || null,
        emergency_contact_name || null, emergency_contact_phone || null,
      );
    }

    res.json({ message: 'Profile updated.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

module.exports = router;
