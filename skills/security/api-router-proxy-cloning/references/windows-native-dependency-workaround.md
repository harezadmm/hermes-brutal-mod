# Windows Native Dependency Workaround

## Problem

On Windows with bleeding-edge Node.js (v24+), native SQLite libraries fail to install:
- `better-sqlite3` - Cannot locate prebuilt binaries for Node v24.19.0
- `sqlite3` - Compilation hangs 120s+ with node-gyp on Windows

**Error:**
```
Error: Could not locate the bindings file. Tried:
 → node_modules/better-sqlite3/build/better_sqlite3.node
 → node_modules/better-sqlite3/lib/binding/node-v137-win32-x64/better_sqlite3.node
```

## Root Cause

- Prebuilt binaries only exist for stable Node.js releases (v18, v20, v22)
- Compiling from source requires:
  - Python 2.7 or 3.x
  - Visual Studio Build Tools (2-4 GB download)
  - node-gyp configured correctly
  - 5-15 minutes compilation time per package

**Not feasible** for quick prototypes or Android Termux environments.

## Solution: Pure JavaScript Database

### Option 1: Custom fs-based JSON Database (Recommended)

**Pros:**
- Zero dependencies
- Works on any Node.js version
- No compilation
- Instant startup

**Implementation:**
```javascript
// lib/db.js
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, '../database/db.json');

function getDb() {
    if (!fs.existsSync(DB_PATH)) {
        const defaultDb = {
            users: [],
            providers: [],
            models: [],
            api_keys: []
        };
        fs.writeFileSync(DB_PATH, JSON.stringify(defaultDb, null, 2));
        return defaultDb;
    }
    return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
}

function saveDb(db) {
    fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function findOne(table, query) {
    const db = getDb();
    return db[table].find(record => 
        Object.keys(query).every(key => record[key] === query[key])
    );
}

function insert(table, data) {
    const db = getDb();
    const newId = db[table].length > 0 
        ? Math.max(...db[table].map(r => r.id || 0)) + 1 
        : 1;
    const record = { id: newId, ...data };
    db[table].push(record);
    saveDb(db);
    return record;
}

module.exports = { getDb, saveDb, findOne, insert };
```

**Performance:**
- 1-1000 records: <10ms read/write
- 1000-10000 records: 10-100ms
- Good enough for API routers (<10K req/day)

### Option 2: lowdb v1.0.0 (JSON file database)

**Note:** lowdb v1.0.0 is the last version supporting CommonJS `require()`. v2+ is ESM-only.

```bash
npm install lowdb@1.0.0
```

```javascript
const low = require('lowdb');
const FileSync = require('lowdb/adapters/FileSync');

const adapter = new FileSync('db.json');
const db = low(adapter);

db.defaults({ users: [], posts: [] }).write();
db.get('users').push({ name: 'Alice' }).write();
```

**Cons:**
- Still requires npm install
- May have compatibility issues with Node v24+

### Option 3: Use older Node.js (v20 LTS)

If you absolutely need better-sqlite3:

```bash
nvm install 20
nvm use 20
npm install better-sqlite3
```

Prebuilt binaries exist for v20.

## When to Use Each

| Use Case | Solution |
|:---------|:---------|
| Quick prototype, no install | Custom fs-based (Option 1) |
| <10K records, simple queries | Custom fs-based (Option 1) |
| Need migrations, complex queries | PostgreSQL/MySQL (separate server) |
| Production, >100K records | PostgreSQL + Prisma |
| Shared hosting (no compile) | MySQL via hosting panel |

## Tested Environment

- **OS:** Windows 10 (MSYS bash via Hermes terminal)
- **Node.js:** v24.19.0 (bleeding edge)
- **npm:** v11.18.0
- **Result:** better-sqlite3 FAILED, custom fs-based JSON WORKED

## Related

- Session: 2026-08-29 UmiAgent Router deployment
- User: Indonesian dev on Android Termux + Windows PC
- Requirement: Zero-friction deployment, no compilation
