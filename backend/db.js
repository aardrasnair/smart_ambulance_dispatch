/**
 * db.js — SQLite via sql.js (pure WebAssembly, zero native compilation).
 *
 * Exposes the same synchronous `.prepare(sql).run/get/all()` API as
 * better-sqlite3 so all route files work unchanged.
 *
 * The on-disk file is `backend/medirush.db` — a standard SQLite database
 * that can be opened with any SQLite client (e.g. DB Browser for SQLite).
 */

const path = require('path');
const fs   = require('fs');

const DB_PATH = path.join(__dirname, 'medirush.db');

let _db = null; // sql.js Database instance

// ── Persist to disk after every write ─────────────────────────────────────────
function _save() {
  const data = _db.export();
  fs.writeFileSync(DB_PATH, Buffer.from(data));
}

// ── Mimic better-sqlite3's prepared-statement API ─────────────────────────────
function _normalise(params) {
  // sql.js expects an array; convert undefined → null
  return (Array.isArray(params) ? params : [params]).map(v => (v === undefined ? null : v));
}

function prepare(sql) {
  return {
    /** Execute (INSERT / UPDATE / DELETE / DDL). Returns {changes}. */
    run(...args) {
      _db.run(sql, _normalise(args));
      _save();
      return { changes: _db.getRowsModified() };
    },
    /** Return the first matching row as a plain object, or undefined. */
    get(...args) {
      const stmt = _db.prepare(sql);
      stmt.bind(_normalise(args));
      const row = stmt.step() ? stmt.getAsObject() : undefined;
      stmt.free();
      return row;
    },
    /** Return all matching rows as an array of plain objects. */
    all(...args) {
      const rows = [];
      const stmt = _db.prepare(sql);
      stmt.bind(_normalise(args));
      while (stmt.step()) rows.push(stmt.getAsObject());
      stmt.free();
      return rows;
    },
  };
}

/** Execute one or more semicolon-separated SQL statements (DDL etc.). */
function exec(sql) {
  _db.exec(sql);
  _save();
}

// ── Async initialisation (call once from server.js before listen) ─────────────
async function init() {
  const initSqlJs = require('sql.js');

  // Point sql.js at the bundled WASM file so it loads correctly in Node
  const SQL = await initSqlJs({
    locateFile: file => path.join(__dirname, 'node_modules', 'sql.js', 'dist', file),
  });

  // Load existing database from disk, or create a fresh one
  if (fs.existsSync(DB_PATH)) {
    _db = new SQL.Database(fs.readFileSync(DB_PATH));
  } else {
    _db = new SQL.Database();
  }

  // Create schema (idempotent)
  _db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id              INTEGER PRIMARY KEY AUTOINCREMENT,
      email           TEXT UNIQUE NOT NULL,
      password_hash   TEXT NOT NULL,
      full_name       TEXT,
      phone           TEXT,
      email_verified  INTEGER DEFAULT 0,
      created_at      TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS user_medical (
      user_id                 INTEGER PRIMARY KEY REFERENCES users(id),
      blood_type              TEXT,
      allergies               TEXT,
      medications             TEXT,
      conditions              TEXT,
      emergency_contact_name  TEXT,
      emergency_contact_phone TEXT
    );

    CREATE TABLE IF NOT EXISTS otps (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      email       TEXT NOT NULL,
      otp         TEXT NOT NULL,
      expires_at  TEXT NOT NULL,
      used        INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS bookings (
      id             INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id        INTEGER NOT NULL REFERENCES users(id),
      request_id     TEXT UNIQUE NOT NULL,
      patient_name   TEXT,
      patient_phone  TEXT,
      location       TEXT,
      emergency_type TEXT,
      ambulance_type TEXT,
      severity_level INTEGER,
      severity_word  TEXT,
      description    TEXT,
      eta_minutes    INTEGER,
      unit_assigned  TEXT,
      status         TEXT DEFAULT 'dispatched',
      created_at     TEXT DEFAULT (datetime('now'))
    );
  `);

  _save(); // write initial schema to disk
  console.log(`💾  Database ready → ${DB_PATH}`);
}

module.exports = { prepare, exec, init };
