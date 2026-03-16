# Aqua Backend API

Backend API untuk sistem manajemen budidaya tambak berbasis multi-tenant. Dibangun menggunakan **FastAPI** + **PostgreSQL**.

---

## Tech Stack

- **Python 3.13**
- **FastAPI** — web framework
- **PostgreSQL** — database
- **SQLAlchemy 2.0** — async ORM
- **Alembic** — database migration
- **JWT** — autentikasi (access + refresh token)
- **Passlib + bcrypt** — hashing password

---

## Struktur Project

```
aqua-backend/
├── alembic_migrations/        # File migrasi database
├── app/
│   ├── api/v1/
│   │   └── routes/            # Endpoint per fitur
│   │       ├── auth.py
│   │       ├── profile.py
│   │       ├── lands.py
│   │       ├── sensors.py
│   │       ├── cultivation.py
│   │       ├── users.py
│   │       └── subscriptions.py
│   ├── core/
│   │   ├── config.py          # Konfigurasi dari .env
│   │   └── security.py        # JWT & password hashing
│   ├── db/
│   │   └── database.py        # Koneksi database async
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic request/response
│   ├── services/              # Business logic
│   ├── utils/
│   │   └── deps.py            # Dependency injection & RBAC
│   └── main.py                # Entry point
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Instalasi & Menjalankan

### 1. Clone & masuk ke folder
```bash
cd aqua-backend
```

### 2. Buat virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install "pydantic[email]" "bcrypt==4.0.1"
```

### 4. Buat file .env
```bash
cp .env.example .env
```
Edit file `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5432/aqua_db
SECRET_KEY=ganti-dengan-string-random-panjang
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Buat database PostgreSQL
```sql
CREATE DATABASE aqua_db;
```

### 6. Jalankan migrasi
```bash
# Windows PowerShell
$env:PYTHONPATH="."; .\venv\Scripts\alembic.exe upgrade head

# Mac/Linux
PYTHONPATH=. alembic upgrade head
```

### 7. Seed data awal (wajib)
Jalankan query berikut di PostgreSQL:
```sql
-- Seed roles
INSERT INTO roles (id, name) VALUES
  (1, 'boss'),
  (2, 'admin'),
  (3, 'teknisi')
ON CONFLICT (id) DO NOTHING;

-- Seed subscription plans
INSERT INTO subscription_plans (id, name, price, duration_days) VALUES
  (gen_random_uuid(), 'Basic', 99000, 30),
  (gen_random_uuid(), 'Pro', 199000, 30),
  (gen_random_uuid(), 'Enterprise', 499000, 30);
```

### 8. Jalankan server
```bash
# Windows PowerShell
$env:PYTHONPATH="."; .\venv\Scripts\uvicorn.exe app.main:app --reload

# Mac/Linux
PYTHONPATH=. uvicorn app.main:app --reload
```

Server berjalan di: **http://localhost:8000**
Swagger UI: **http://localhost:8000/docs**

---

## Role & Akses

| Role | ID | Deskripsi |
|---|---|---|
| Boss | 1 | Pemilik company, akses penuh |
| Admin | 2 | Kelola lahan, kolam, sensor |
| Teknisi | 3 | Input data sensor & budidaya |

### Matriks Akses

| Fitur | Boss | Admin | Teknisi |
|---|---|---|---|
| Lands & Ponds — baca | ✅ | ✅ | ✅ |
| Lands & Ponds — tulis | ✅ | ✅ | ❌ |
| Sensors — baca | ✅ | ✅ | ✅ |
| Sensors — tulis | ✅ | ✅ | ❌ |
| Sensor Logs — semua | ✅ | ✅ | ✅ |
| Cultivation Records — baca/input | ✅ | ✅ | ✅ |
| Cultivation Records — hapus | ✅ | ✅ | ❌ |
| Opex — baca | ✅ | ✅ | ✅ |
| Opex — tulis | ✅ | ✅ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| Subscription | ✅ | ❌ | ❌ |
| Profile Company — update | ✅ | ❌ | ❌ |

---

## Endpoint API

### Auth
| Method | Endpoint | Deskripsi |
|---|---|---|
| POST | `/api/v1/auth/register` | Register user + company baru |
| POST | `/api/v1/auth/login` | Login, dapat access + refresh token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Data user yang sedang login |
| POST | `/api/v1/auth/forgot-password` | Request token reset password |
| POST | `/api/v1/auth/reset-password` | Reset password via token |
| PUT | `/api/v1/auth/change-password` | Ganti password |

### Profile
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/profile` | Lihat profil user + company |
| PUT | `/api/v1/profile` | Update nama/email |
| GET | `/api/v1/profile/company` | Lihat profil company |
| PUT | `/api/v1/profile/company` | Update company (boss only) |

### Lands & Ponds
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/lands` | List semua lahan |
| POST | `/api/v1/lands` | Buat lahan baru |
| GET | `/api/v1/lands/{id}` | Detail lahan |
| PUT | `/api/v1/lands/{id}` | Update lahan |
| DELETE | `/api/v1/lands/{id}` | Hapus lahan |
| GET | `/api/v1/lands/{id}/ponds` | List kolam di lahan |
| POST | `/api/v1/lands/{id}/ponds` | Buat kolam baru |
| GET | `/api/v1/lands/{id}/ponds/{pond_id}` | Detail kolam |
| PUT | `/api/v1/lands/{id}/ponds/{pond_id}` | Update kolam |
| DELETE | `/api/v1/lands/{id}/ponds/{pond_id}` | Hapus kolam |

### Sensors & Logs
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/ponds/{pond_id}/sensors` | List sensor di kolam |
| POST | `/api/v1/ponds/{pond_id}/sensors` | Tambah sensor |
| GET | `/api/v1/ponds/{pond_id}/sensors/{id}` | Detail sensor |
| PUT | `/api/v1/ponds/{pond_id}/sensors/{id}` | Update sensor |
| DELETE | `/api/v1/ponds/{pond_id}/sensors/{id}` | Hapus sensor |
| GET | `/api/v1/ponds/{pond_id}/sensors/{id}/logs` | List log sensor |
| POST | `/api/v1/ponds/{pond_id}/sensors/{id}/logs` | Input log harian |
| GET | `/api/v1/ponds/{pond_id}/sensors/{id}/logs/{log_id}` | Detail log |
| PUT | `/api/v1/ponds/{pond_id}/sensors/{id}/logs/{log_id}` | Update log |
| DELETE | `/api/v1/ponds/{pond_id}/sensors/{id}/logs/{log_id}` | Hapus log |

### Cultivation Items (Master Data)
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/cultivation-items` | List semua item |
| POST | `/api/v1/cultivation-items` | Tambah item baru |
| GET | `/api/v1/cultivation-items/{id}` | Detail item |
| PUT | `/api/v1/cultivation-items/{id}` | Update item |
| DELETE | `/api/v1/cultivation-items/{id}` | Hapus item |

### Cultivation Records
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/ponds/{pond_id}/cultivation-records` | List record budidaya |
| POST | `/api/v1/ponds/{pond_id}/cultivation-records` | Input record budidaya |
| GET | `/api/v1/ponds/{pond_id}/cultivation-records/{id}` | Detail record |
| PUT | `/api/v1/ponds/{pond_id}/cultivation-records/{id}` | Update record |
| DELETE | `/api/v1/ponds/{pond_id}/cultivation-records/{id}` | Hapus record |

### Opex Records
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/ponds/{pond_id}/opex-records` | List opex per kolam |
| POST | `/api/v1/ponds/{pond_id}/opex-records` | Input biaya opex |
| GET | `/api/v1/ponds/{pond_id}/opex-records/{id}` | Detail opex |
| PUT | `/api/v1/ponds/{pond_id}/opex-records/{id}` | Update opex |
| DELETE | `/api/v1/ponds/{pond_id}/opex-records/{id}` | Hapus opex |

### User Management
| Method | Endpoint | Deskripsi | Akses |
|---|---|---|---|
| GET | `/api/v1/users/roles` | List semua role | Semua |
| GET | `/api/v1/users` | List user dalam company | Semua |
| POST | `/api/v1/users/invite` | Undang admin/teknisi | Boss |
| PUT | `/api/v1/users/{id}` | Update role/nama user | Boss |
| DELETE | `/api/v1/users/{id}` | Hapus user dari company | Boss |

### Subscription
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/subscriptions/plans` | List paket subscription |
| GET | `/api/v1/subscriptions/active` | Subscription aktif company |
| GET | `/api/v1/subscriptions/history` | Riwayat subscription |
| GET | `/api/v1/subscriptions/payments` | Riwayat pembayaran |

---

## Autentikasi

Semua endpoint (kecuali register, login, forgot-password, reset-password) memerlukan JWT token.

Sertakan token di header setiap request:
```
Authorization: Bearer <access_token>
```

Access token expired dalam **30 menit**. Gunakan refresh token untuk mendapatkan access token baru via `POST /api/v1/auth/refresh`.

---

## Environment Variables

| Variable | Deskripsi | Default |
|---|---|---|
| `DATABASE_URL` | URL koneksi PostgreSQL async | wajib diisi |
| `SECRET_KEY` | Secret key untuk JWT | wajib diisi |
| `ALGORITHM` | Algoritma JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durasi access token | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durasi refresh token | `7` |