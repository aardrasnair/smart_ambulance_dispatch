const router  = require('express').Router();
const bcrypt   = require('bcryptjs');
const jwt      = require('jsonwebtoken');
const nodemailer = require('nodemailer');
const db       = require('../db');

const JWT_SECRET = process.env.JWT_SECRET || 'medirush_jwt_secret_change_in_production';

// Build a nodemailer transport if SMTP is configured, otherwise fall back to console
function getTransporter() {
  if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS) {
    return nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: false,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
  }
  return null;
}

async function sendOTP(email, otp) {
  const transporter = getTransporter();
  if (!transporter) {
    console.log(`\n📧  OTP for ${email}: ${otp}  (SMTP not configured — logged to console)\n`);
    return;
  }
  await transporter.sendMail({
    from: process.env.FROM_EMAIL || process.env.SMTP_USER,
    to: email,
    subject: 'MediRush — Your verification code',
    html: `
      <div style="font-family:sans-serif;max-width:420px;margin:0 auto;padding:32px 24px">
        <h2 style="color:#d63031;margin:0 0 8px">🚑 MediRush</h2>
        <p style="color:#4a5568;margin:0 0 24px">Smart Ambulance Dispatch</p>
        <p>Your verification code is:</p>
        <div style="font-size:40px;font-weight:700;letter-spacing:10px;color:#d63031;margin:20px 0;font-family:monospace">${otp}</div>
        <p style="color:#888;font-size:13px">This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
      </div>
    `,
  });
}

// ── POST /api/auth/register ───────────────────────────────────────────────────
router.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password)
      return res.status(400).json({ error: 'Email and password are required.' });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      return res.status(400).json({ error: 'Please enter a valid email address.' });
    if (password.length < 6)
      return res.status(400).json({ error: 'Password must be at least 6 characters.' });

    const existing = db.prepare('SELECT id, email_verified FROM users WHERE email = ?').get(email);
    if (existing?.email_verified)
      return res.status(400).json({ error: 'This email is already registered. Please sign in.' });

    const hash = await bcrypt.hash(password, 10);

    if (existing) {
      // Re-register unverified account: update password
      db.prepare('UPDATE users SET password_hash = ? WHERE email = ?').run(hash, email);
    } else {
      db.prepare('INSERT INTO users (email, password_hash) VALUES (?, ?)').run(email, hash);
    }

    // Invalidate old OTPs and generate a new one
    db.prepare('UPDATE otps SET used = 1 WHERE email = ? AND used = 0').run(email);
    const otp = String(Math.floor(100000 + Math.random() * 900000));
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString();
    db.prepare('INSERT INTO otps (email, otp, expires_at) VALUES (?, ?, ?)').run(email, otp, expiresAt);

    await sendOTP(email, otp);

    res.json({ message: 'Verification code sent to your email.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

// ── POST /api/auth/verify-otp ─────────────────────────────────────────────────
router.post('/verify-otp', (req, res) => {
  try {
    const { email, otp } = req.body;
    if (!email || !otp)
      return res.status(400).json({ error: 'Email and OTP are required.' });

    const record = db
      .prepare('SELECT * FROM otps WHERE email = ? AND used = 0 ORDER BY id DESC LIMIT 1')
      .get(email);

    if (!record)
      return res.status(400).json({ error: 'No pending code. Please register again.' });
    if (new Date(record.expires_at) < new Date())
      return res.status(400).json({ error: 'Code has expired. Please register again.' });
    if (record.otp !== otp.trim())
      return res.status(400).json({ error: 'Incorrect code. Please try again.' });

    db.prepare('UPDATE otps SET used = 1 WHERE id = ?').run(record.id);
    db.prepare('UPDATE users SET email_verified = 1 WHERE email = ?').run(email);

    res.json({ message: 'Email verified successfully.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

// ── POST /api/auth/complete-profile ──────────────────────────────────────────
router.post('/complete-profile', (req, res) => {
  try {
    const {
      email, full_name, phone,
      blood_type, allergies, medications, conditions,
      emergency_contact_name, emergency_contact_phone,
    } = req.body;

    if (!email || !full_name)
      return res.status(400).json({ error: 'Email and full name are required.' });

    const user = db.prepare('SELECT id, email_verified FROM users WHERE email = ?').get(email);
    if (!user)         return res.status(400).json({ error: 'User not found.' });
    if (!user.email_verified) return res.status(400).json({ error: 'Email not verified.' });

    db.prepare('UPDATE users SET full_name = ?, phone = ? WHERE id = ?')
      .run(full_name, phone || null, user.id);

    const hasMedical = db.prepare('SELECT user_id FROM user_medical WHERE user_id = ?').get(user.id);
    if (hasMedical) {
      db.prepare(`
        UPDATE user_medical
        SET blood_type=?, allergies=?, medications=?, conditions=?,
            emergency_contact_name=?, emergency_contact_phone=?
        WHERE user_id=?
      `).run(
        blood_type || null, allergies || null, medications || null, conditions || null,
        emergency_contact_name || null, emergency_contact_phone || null,
        user.id,
      );
    } else {
      db.prepare(`
        INSERT INTO user_medical
          (user_id, blood_type, allergies, medications, conditions,
           emergency_contact_name, emergency_contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(
        user.id,
        blood_type || null, allergies || null, medications || null, conditions || null,
        emergency_contact_name || null, emergency_contact_phone || null,
      );
    }

    const token = jwt.sign({ id: user.id, email }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ token, user: { id: user.id, email, full_name, phone: phone || null } });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

// ── POST /api/auth/login ──────────────────────────────────────────────────────
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password)
      return res.status(400).json({ error: 'Email and password are required.' });

    const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
    if (!user) return res.status(401).json({ error: 'Invalid email or password.' });
    if (!user.email_verified)
      return res.status(401).json({ error: 'Please verify your email before signing in.' });

    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) return res.status(401).json({ error: 'Invalid email or password.' });

    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
    res.json({
      token,
      user: { id: user.id, email: user.email, full_name: user.full_name, phone: user.phone },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

module.exports = router;
