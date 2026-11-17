# Equipment Library — MySQL / Docker Compose

Δύο containers, `app` (FastAPI/Python) και `db` (MySQL 8.4).
Το MySQL αντίγραφο είναι ανεξάρτητο από τις εγκαταστάσεις SQLite/PostgreSQL.
Τα migrations δημιουργούν τον προεπιλεγμένο administrator `admin`
με κωδικό `QWErty123!@#` (αποθηκευμένο ως hash). Η εφαρμογή ανοίγει στο login.
Η ροή `/setup` έχει αφαιρεθεί. Αν υπάρχει ήδη χρήστης `admin`, διατηρούνται
τα στοιχεία του. Οι επόμενες εκκινήσεις δεν επαναφέρουν τον κωδικό.

## Εκκίνηση

Άνοιξε Docker Desktop σε Linux containers και PowerShell σε αυτόν τον φάκελο.

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f app
```

Άνοιξε http://127.0.0.1:8005.
Το app περιμένει να είναι έτοιμη η βάση, εφαρμόζει Alembic migrations και ξεκινά.

## MySQL Workbench

Δημιούργησε σύνδεση με Standard TCP/IP.

| Ρύθμιση | Τιμή |
|---|---|
| Hostname | 127.0.0.1 |
| Port | 3307 |
| Username | equipment |
| Password | local-development-only |
| Default schema | equipment |

Το app συνδέεται εσωτερικά στο `db:3306`. Η θύρα 3307 είναι δεσμευμένη
μόνο στο localhost. Το Workbench συνδέεται απευθείας στον MySQL server.

## Δεδομένα και κωδικοί

- Volume `database` για τη MySQL στο `/var/lib/mysql`.
- Volume `app-files` για φωτογραφίες, PDF και backups.
- Προαιρετικά αντέγραψε `.env.example` σε `.env` πριν την πρώτη εκκίνηση.
  Χρησιμοποίησε URL-safe κωδικό για `MYSQL_PASSWORD`.
- Οι προεπιλεγμένοι κωδικοί προορίζονται για τοπική ανάπτυξη.
  Η αλλαγή μεταβλητών μετά τη δημιουργία του volume δεν αλλάζει τους κωδικούς
  υπαρχόντων MySQL χρηστών. Χρησιμοποίησε ALTER USER για υπάρχουσα βάση.
- Η εφαρμογή χρησιμοποιεί τον χρήστη `equipment`, ενώ ο root χρησιμοποιείται
  για αρχική διαχείριση. Για παραγωγή χρειάζεται κατάλληλος διαχωρισμός δικαιωμάτων.
- Το utf8mb4 υποστηρίζει ελληνικά και η προεπιλεγμένη collation κάνει
  αναζήτηση και μοναδικά ονόματα/κωδικούς χωρίς διάκριση πεζών/κεφαλαίων και τόνων.
- Τα πεδία ονομάτων/κωδικών που συμμετέχουν σε indexes έχουν όριο 255
  χαρακτήρων. Οι περιγραφές και οι σημειώσεις διατηρούν τύπο TEXT.

```powershell
docker compose stop
docker compose start
docker compose down
```

Τα δεδομένα παραμένουν. Το `docker compose down --volumes` διαγράφει
οριστικά βάση και αρχεία αυτής της εγκατάστασης.

## Backup

Το ZIP από τις Ρυθμίσεις περιέχει `data/equipment.sql` και uploads.
Η εφαρμογή χρησιμοποιεί το συμβατό `mariadb-dump` client για SQL export
από MySQL, με single transaction για συνεπές snapshot των InnoDB πινάκων.
Για επαναφορά χρησιμοποίησε SQL import σε άδεια βάση και επανάφερε
ξεχωριστά τα uploads στο volume. Προτίμησε περίοδο χωρίς αλλαγές αρχείων
για συντονισμένο backup βάσης και uploads.

## Έλεγχοι

Οι δοκιμές απαιτούν ξεχωριστή βάση `equipment_test` και αρνούνται να
εκτελεστούν στην κανονική βάση. Χρησιμοποίησε τον root με `mysql -u root -p`
μέσα στο db container για δημιουργία της βάσης και GRANT δικαιωμάτων
στον `equipment` αποκλειστικά για `equipment_test.*`.

```powershell
docker compose run --rm --user root -v "${PWD}/tests:/app/tests:ro" -e ELM_DATABASE_URL=mysql+pymysql://equipment:local-development-only@db:3306/equipment_test app sh -c "pip install pytest==8.3.5 httpx==0.28.1 && python -m pytest tests/test_workflows.py -q"
```

Οι εγγραφές της εφαρμογής κλειδώνουν τη σταθερή εγγραφή app_settings με
SELECT FOR UPDATE. Το READ COMMITTED επιτρέπει στην επόμενη συναλλαγή να
διαβάσει την ολοκληρωμένη χρέωση αφού αποκτήσει το lock. Commit/rollback
απελευθερώνουν το lock.
