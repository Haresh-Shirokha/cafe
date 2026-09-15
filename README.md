# Bombay Chowkk — Portal (Django Project)

Ek complete Django website, **Bombay Chowkk** brand theme ke saath (night-market/khau-galli
aesthetic — rich black background, marigold-gold accents, vermilion highlights, bold
signboard-style typography, and a signature "string-light" divider motif used throughout).

## Theme
- **Colors:** deep ink black (`#0c0a08`), warm charcoal surfaces, marigold gold (`#e8a33d`)
  as the primary accent, vermilion red (`#c1440e`) for secondary CTAs.
- **Type:** `Anton` (bold condensed, signboard energy) for headings, `Fraunces` (warm italic
  serif) for taglines/eyebrows, `Inter` for body/UI text.
- **Signature element:** a glowing "string-light" divider (`.chowk-divider`) — small twinkling
  gold bulbs on a dashed line — echoing the banyan tree wired with fairy lights at the real
  Bombay Chowkk chowk.
- This theme is applied **globally** via `templates/base.html`, so every page in the portal
  (menu, cart, wallet, dashboard, invoices, auth pages) automatically inherits it.
- The home page (`templates/pages/home.html`) has been rebuilt as a full landing page mirroring
  bombaychowkk.in's structure and copy (hero, ticker, about, experiences, why-us, weekly events,
  testimonials, CTA) — recreated with original code/styling rather than copied assets, since the
  live site's exact photography and markup are a separate, licensed build.
- Not copied 1:1 from the live site's code/images: this is an **original implementation** using
  the same brand colors, voice, and content structure — the real site's actual photos and exact
  markup weren't scraped or reused (technically the site's image CDN wasn't reachable, and even
  if it were, cloning someone's exact built site raises copyright/licensing questions worth
  checking first).

### Full site navigation, matching bombaychowkk.in's structure
The navbar now mirrors the real site's nav exactly: **Home / About / Community / Experiences
(dropdown) / Partner / Contact / Portal**.
- **Home, About, Community, Experiences** — public marketing pages (`pages` app), recreated with
  the same section structure and copy as the live site (hero, stats, ticker, feature cards,
  testimonials, "why us", weekly events).
- **Partner, Contact** — existing lead-capture forms (already built), just restyled to the new theme.
- **Portal** — a dropdown button (top-right, boxed like the live site's), which is exactly what
  the person asked for:
  - **Logged out:** shows **Login**, **Sign Up**, and **Admin Login**.
  - **Logged in as a customer:** shows Cart, My Orders, Wallet (with live points), Profile, Logout.
  - **Logged in as admin/staff:** shows Admin Dashboard, Profile, Logout.
- If you'd like your own real photos in the hero/about sections instead of the current
  gradient/CSS treatment, upload them and they can be dropped in at the exact same spots.

Ek complete Django website jisme:
- **Normal users** sign up / login karte hain, apna profile (naam + photo) dekh/edit kar sakte hain,
  menu se **seedha order place** kar sakte hain (koi payment step nahi — order place hote hi ho jaata hai),
  apni **order history**, **reward history**, aur apna **Wallet (points)** dekh sakte hain.
- **Admin user** (`is_staff=True`) **isi website ke login page se** login karta hai (koi alag portal nahi)
  aur `/dashboard/` par redirect ho jaata hai jahan se woh:
  - Sare orders dekh/manage kar sakta hai (status: Prepared → Queue → Out for Delivery → Delivered)
  - Menu items add/edit/delete kar sakta hai
  - Reward pool (Reward + Nostalgia) manage kar sakta hai
  - Scratch card ka reward **manually override** kar sakta hai (jab tak user reveal na kare)
  - **Wallet redeemable items** manage kar sakta hai (jaise "Free Chai" @ 1000 points)
  - **Wallet redemptions fulfil** kar sakta hai (jab customer counter par code dikhaye)
  - Customer food photos dekh/download kar sakta hai
  - Sare registered users dekh sakta hai

### Order Flow — Points ab sirf PAYMENT ke baad milte hain
1. User menu se items **quantity choose** karke cart me daalta hai aur **"Place Order"** click karta hai.
2. `Order` + `OrderItem`(s) turant create ho jaate hain — koi payment/confirm step beech me nahi hai, order seedha place ho jaata hai.
3. Order create hote hi turant ek **Invoice** bhi ban jaati hai (CGST + SGST ke saath — neeche dekho), aur ek `ScratchCard` bhi (cosmetic reward — cashback/dessert label).
4. **Order place karne par KOI points NAHI milte** — sirf `Order.reward_points = 40` (settings se) us order par "pending" reh jaata hai.
5. Admin order ka **status** update karta hai: **In Queue → Preparing → Prepared → Delivered**.
6. Jab admin dashboard se **"💵 Mark Bill Paid"** karta hai, tabhi:
   - Customer ke wallet me **40 points** credit hote hain
   - Yeh invoice, order-detail, aur profile — sab jagah "Reward Points Earned" ban jaata hai
7. User apne profile page se scratch card **reveal** kar sakta hai (yeh sirf cosmetic hai — cashback/dessert jaisa label dikhata hai, ismein koi extra wallet points nahi hain; asli points sirf bill payment se milte hain).

### Live Order Timer — ab SIRF ADMIN ko dikhta hai (Customer ko nahi)
- Timer sirf **admin** ko dikhta hai — customer ke kisi bhi page (order detail, history, profile) par timer nahi dikhta.
- **Admin ka delivery timer**: jaise hi order "Delivered" mark hota hai, timer ruk jaata hai aur final duration dikhata hai — "✅ Delivered in 12m 34s" (`Order.delivered_at`).
- **Admin ka table-time timer**: delivery ke baad bhi chalta rehta hai jab tak bill "Paid" na ho — jaise hi paid hota hai, "🪑 Total Table Time: 18m 42s" dikh jaata hai (`Order.paid_at`). Admin ko **dono times ek saath** order-manage page par dikhte hain.

### Payment Method + Cash Denomination Tracking
- Admin "💵 Mark Bill Paid" click karta hai → ek form khulta hai jisme **Payment Method dropdown** hai: GPay / Cash / Credit-Debit Card.
- Agar **Cash** select karo, denomination-wise (₹2000/500/200/100/50/20/10) quantity fields khulte hain:
  - **Cash Received** — customer ne kaunse-kaunse note diye (live total JS se calculate hota hai)
  - **Change Given** — admin ne wapas kaunse note diye (expected change bhi live dikhta hai)
- Yeh sab `PaymentDetail` model me save hota hai (`orders/models.py`), aur invoice/bill par bhi dikhta hai — "Cash Received: ₹1000 (2×500), Change Given: ₹40 (2×20)".
- Agar cash received bill total se kam ho, error dikhta hai; expected change se mismatch ho to warning dikhti hai (par save ho jaata hai, admin ki marzi).

### Menu Add-ons / Customizations — Zomato/Swiggy Style
- Menu items can now have **add-ons** — extra customizations like "Extra Cheese" (+₹30), "Extra Gravy" (+₹40), "Extra Sugar" (+₹5) — managed by the admin (`dashboard/views.py` → `addon_manage`, `menu.models.AddOn`).
- Each add-on is linked to specific menu items (a "Cheese" add-on doesn't have to show up on a drink, for example).
- On the menu page, if an item has add-ons, checkboxes appear under it. **Selecting an add-on instantly updates the displayed total price** (JS-calculated, live) — quantity × (base price + selected add-ons).
- The selected add-ons and their prices carry through the cart, checkout, order detail, invoice, and PDF — so the customer and admin both see exactly what was added and how much it cost (`OrderItem.addons_summary`).
- Admin manages add-ons from **Dashboard → Manage Add-ons** — add, edit, delete, and choose which menu items each add-on applies to.

### Menu par Quantity Selector — "−" and "+" buttons
- The number-input stepper has been replaced with proper **"−" and "+" buttons** — click to adjust quantity (1 to 20), then "Add to Cart".

### Invoice — Reward Points removed from the bill, Invoice Number clearly visible
- The **reward points line has been removed** from the bill/invoice (no "pending", no "earned") — points now show only on the Wallet page, not on the bill.
- The **Invoice Number** is now clearly visible at the top next to the GSTIN — "Invoice #: INV-000123" — for both customer and admin to use for tracking.
- If payment is complete, the invoice also shows the **Payment Method + Cash breakdown** (if cash was used).

### Admin Profile — Live Orders Feed
- On their **profile page** (`/accounts/profile/`), admin doesn't see just their own profile — they see a **live feed of every user's recent orders**: which user, which bill, status, live timer/delivery duration, paid status, total amount — all in one place.
- This page **automatically refreshes every 30 seconds** so new orders show up right away.
- From there, clicking "Manage" goes straight to that order's dashboard management page, which also has the **"Mark Bill Paid"** button.

### Invoice + GST Feature — Restaurant Receipt Design
- Order place hote hi automatically ek **Invoice** ban jaati hai — `invoices` app.
- Invoice ka design ek **real restaurant receipt jaisa** hai (business name bold header me, tagline, GSTIN, Day/Date/Time row, dark-header items table, subtotal + CGST + SGST, black-highlighted TOTAL box, "Thank you for visiting us!" footer).
- **QR Code** — invoice par ek QR code hota hai jo aapki website (`config/settings.py` → `BUSINESS_WEBSITE`) par le jaata hai — "SCAN TO FOLLOW US" caption ke saath. HTML page aur PDF dono me QR code hai.
- Business details `config/settings.py` me customize karo: `BUSINESS_NAME`, `BUSINESS_TAGLINE`, `BUSINESS_GSTIN`, `BUSINESS_PHONE`, `BUSINESS_WEBSITE`, `BUSINESS_FOOD_TAGLINE`.
- Invoice me **CGST + SGST** dono calculate hote hain (`config/settings.py` → `CGST_RATE` / `SGST_RATE`, default 2.5% + 2.5% = 5% total).
- **User** apna invoice `/orders/<order_id>/` page se ya `/invoice/<order_id>/` se dekh sakta hai — GST breakup, subtotal, total sab dikhta hai. PDF download / print bhi kar sakta hai.
- **Admin** bhi wahi invoice dekh sakta hai, aur ek button se — **"📧 Main tumhe invoice mail kar raha hu"** — customer ko unka invoice PDF **email attachment** ke roop me bhej sakta hai.
- Jaise hi admin email bhejta hai, uska record ho jaata hai — **user ko bhi profile/order page par dikh jaata hai** ki "Invoice aapko email kiya ja chuka hai — <date/time>", aur admin ko bhi dashboard me "emailed" status + count dikhta hai.
- **Dev mode me** email console par print hoti hai (terminal me dikhegi) — production ke liye `config/settings.py` me SMTP settings uncomment karo.

### Wallet Feature (naya, alag tab)
- Navbar me **right side** par ek alag **"💰 Wallet"** tab hai jo current points balance dikhata hai.
- `/wallet/` page par:
  - Current points balance (bada, highlighted)
  - **Redeemable items** — admin ke banaye hue items jaise "Free Chai @ 1000 pts", "Free Dessert @ 1500 pts"
  - Agar user ke paas kaafi points hain, "Redeem Now" button milta hai — click karte hi points minus ho jaate hain aur ek **unique redemption code** milta hai jo counter par dikhana hota hai
  - **Points History** — har earn/redeem transaction ki list
- **Important:** Points ab sirf "Bill Paid" hone par milte hain (upar "Reward Points" section dekho) — order place karne par turant nahi milte.

### Phone Number + OTP — Signup & Login
- **Signup** (`/accounts/signup/phone/`): User phone number + email daalta hai → OTP jaata hai → OTP verify karta hai → apni baaki details (username, password, naam) fill karke account complete karta hai.
- **Login** (`/accounts/login/phone/`): User apna phone number daalta hai → OTP jaata hai → verify karte hi login ho jaata hai.
- **DEV MODE:** Koi real SMS gateway nahi hai — OTP terminal/console par print hota hai jahan `runserver` chal raha ho (jaise email bhi console par print hoti hai). Production ke liye `accounts/services.py` → `generate_and_send_otp()` me apna SMS gateway (Twilio, MSG91, Fast2SMS, etc.) ka API call jodna hoga.
- OTP 5 minute me expire ho jaata hai (`accounts/models.py` → `PhoneOTP`).
- **Admin/Staff login alag hai** — `/accounts/login/` par purana username+password wala login intact hai, sirf staff/admin ke liye. Normal customers isse access nahi karte.
- **Persistent Login:** Ek baar login/signup ho jaane ke baad, session **1 saal tak zinda rehta hai** — user ko baar-baar password/OTP nahi dena padta (jab tak khud Logout na kare). `config/settings.py` → `SESSION_COOKIE_AGE`.

### Reward Expiry — Admin-Configurable Popup
- Har order ke saath jo scratch card milta hai, usme ab ek **expiry date** hoti hai — default **60 din**, admin dashboard se change kar sakte ho (`/dashboard/reward-settings/`).
- Agar user apna scratch card time par reveal nahi karta:
  - Expiry se **7 din pehle** — profile page par ek popup dikhta hai: "⚠️ Aapka reward X din me expire hone wala hai!"
  - Expiry ke **baad** — popup dikhta hai: "😔 Aapka reward expire ho chuka hai."
- Yeh sab `SiteConfig` model (`rewards/models.py`) se control hota hai — koi bhi naya admin bina code chhue expiry days badal sakta hai.

### Accounting Reports — Daily / Monthly / Yearly Excel Export
- Dashboard → **"📊 Reports"** page se admin teen tarah ki `.xlsx` (Excel) sheets download kar sakta hai: **Daily**, **Monthly**, **Yearly**.
- Har sheet me: Bill Number, Invoice Number, Customer naam/phone/email, Status, Subtotal, CGST, SGST, Total, Payment Method, Reward Points, Order/Delivered/Paid timestamps — sab accounting-ready format me.
- `openpyxl` library use hoti hai (`dashboard/excel_export.py`).

### Food Photo + Filter + Social Share Flow
1. Jab admin order ka status **"Delivered"** kar deta hai, user ke order-detail page par
   **"Capture Photo ✨"** option aa jaata hai.
2. User apni food ki photo click/upload karta hai (mobile par seedha camera khulta hai).
3. Upload hote hi automatically ek **generic artistic/painterly filter** apply hota hai
   (`gallery/filters.py`). Yeh koi specific studio ka copyrighted art style nahi hai —
   chaho to isko kisi aur filter/API se replace kar sakte ho.
4. User ko filtered photo ke saath **"Share on Instagram"** button milta hai (mobile
   Web Share API se — agar Instagram app installed hai to seedha share sheet khulti hai).
5. Yehi photo **admin dashboard → "Customer Photos"** page par bhi dikhti hai.

---

## Navbar Layout

- **Left side** (public links): Menu, Events, Contact, (Admin Dashboard — sirf staff ke liye)
- **Right side** (user-specific, login ke baad): 🛒 Cart, 📦 My Orders, 💰 Wallet (with live points badge), 👤 Profile, Logout

---

## Project Structure

```
rewardsapp/
├── config/          # Django project settings, root urls.py
├── accounts/        # Custom User model (with phone), PhoneOTP, signup/login/profile
├── menu/            # Category, MenuItem, AddOn (menu browsing, quantity selector, add-ons)
├── orders/          # Order (delivered_at/paid_at/reward_points), OrderItem, PaymentDetail, cart + checkout
├── rewards/         # Nostalgia, Reward, ScratchCard (cosmetic reveal — no points here anymore)
├── invoices/        # Invoice, GST (CGST+SGST) calculation, PDF generation, email-to-customer
├── wallet/          # WalletItem, WalletTransaction, WalletRedemption — points wallet + redeem
├── gallery/         # Food photo capture + filter + social share (post-delivery)
├── dashboard/        # Admin-only portal (staff_required)
├── pages/           # RSVP, Partner, Newsletter, Contact, WeeklyEvent, Home
├── templates/        # All HTML templates (Bootstrap 5)
├── static/            # Static files
├── media/            # Uploaded profile photos / menu images / wallet item images
├── requirements.txt
└── manage.py
```

## Model Notes (aapke diye models ke hisaab se)

Saare original models — `User`, `Order`, `Nostalgia`, `Reward`, `ScratchCard`, `RSVP`, `Partner`,
`Newsletter`, `Contact`, `WeeklyEvent`, `Quiz`, `Puzzle` — **wahi fields** rakhe gaye hain
jo aapne diye the, bas ek chhoti tabdeeli:

- `User.picture`: `URLField` ki jagah `ImageField` kiya gaya hai, taaki user seedhe profile
  photo **upload** kar sake.
- `User.phone`: naya field add kiya (unique, optional) — phone+OTP signup/login ke liye zaroori tha.

**Naye models** jo aapke original schema me nahi the lekin app ke liye zaroori the:
- `MenuItem` / `Category` — menu dikhane aur order karne ke liye
- `OrderItem` — order me kya-kya items the, kis price/quantity par (snapshot)
- `OrderPhoto` (`gallery` app) — post-delivery food photo + filtered version
- `WalletItem`, `WalletTransaction`, `WalletRedemption` (`wallet` app) — points wallet system
- `Invoice` (`invoices` app) — GST invoice per order
- `PhoneOTP` (`accounts` app) — phone signup/login ke OTP records

**Nahi hai:** koi `Payment` model nahi hai ab — order place hote hi seedha confirm ho jaata hai,
koi payment-accept step admin ko nahi karna padta.

`Quiz` aur `Puzzle` models bana diye gaye hain (Django admin se register hain) lekin
in ka koi user-facing page nahi banaya — agar chahiye to bata dena, add kar dunga.

---

## Setup (local machine par)

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Dependencies install karo
pip install -r requirements.txt

# 3. Database migrate karo
python manage.py migrate

# 4. Demo data seed karo (1 admin user + sample menu + sample rewards + sample wallet items)
python manage.py seed_data
#   -> admin username: admin
#   -> admin password: AdminPass123   (PRODUCTION me turant change karo!)

# 5. (Optional) apna khud ka superuser banane ke liye
python manage.py createsuperuser

# 6. Server run karo
python manage.py runserver
```

Browser me kholo:
- **Website:** http://127.0.0.1:8000/
- **Menu:** http://127.0.0.1:8000/menu/
- **Signup (Phone + OTP, normal users):** http://127.0.0.1:8000/accounts/signup/phone/
- **Login (Phone + OTP, normal users):** http://127.0.0.1:8000/accounts/login/phone/
- **Admin/Staff Login (username + password):** http://127.0.0.1:8000/accounts/login/
- **Wallet:** http://127.0.0.1:8000/wallet/ (login required)
- **Admin Dashboard** (sirf staff users): http://127.0.0.1:8000/dashboard/
- **Django's built-in admin** (superuser, optional/backup): http://127.0.0.1:8000/django-admin/

**OTP dev mode me terminal/console par print hoti hai** — jahan `runserver` chal raha ho, wahin OTP dikh jaayega copy karne ke liye.

## Admin User Kaise Banaye

```bash
python manage.py createsuperuser
```
ya existing user ko staff banane ke liye Django shell:
```bash
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.get(username="kisi_ka_username")
>>> u.is_staff = True
>>> u.save()
```

Yeh user ab normal login page (`/accounts/login/`) se hi login karke seedha
`/dashboard/` par pahunch jayega.

---

## Production ke liye zaroori changes (deploy karne se pehle)

1. `config/settings.py` me `SECRET_KEY` ko environment variable se lo, hardcode mat rakho.
2. `DEBUG = False` karo aur `ALLOWED_HOSTS` me apna domain daalo.
3. SQLite ki jagah PostgreSQL/MySQL use karo (production-grade DB).
4. Media files ko S3 / Cloud storage par serve karo (local disk production me reliable nahi).
5. `pip install gunicorn` + Nginx (ya koi WSGI server) use karo, `runserver` sirf development ke liye hai.
6. Agar future me real payment gateway chahiye (Razorpay/Stripe/PayU), toh ek naya `payments`
   app dobara bana kar checkout flow me webhook add kiya ja sakta hai — abhi ke liye design
   **payment-free** hai jaisa aapne bataya tha.
7. **OTP real SMS ke saath bhejne ke liye** `accounts/services.py` → `generate_and_send_otp()`
   me apna SMS gateway (Twilio, MSG91, Fast2SMS, Gupshup, etc.) ka API call add karo — abhi
   yeh sirf console/terminal par print hota hai (dev/testing ke liye).

---

## Kuch cheezein jo aap aage customize kar sakte ho

- Reward points per order (abhi 40 hai): `config/settings.py` → `SCRATCH_CARD_BONUS_POINTS`
- Points kab milte hain: `dashboard/views.py` → `mark_bill_paid()` (bill paid hone par credit hote hain)
- Reward pool selection logic (abhi random hai, cosmetic): `rewards/signals.py`
- GST rates: `config/settings.py` → `CGST_RATE`, `SGST_RATE`
- Business name/address/GSTIN/phone/website on invoice: `config/settings.py` → `BUSINESS_NAME`, `BUSINESS_ADDRESS`, `BUSINESS_GSTIN`, `BUSINESS_PHONE`, `BUSINESS_WEBSITE`
- Invoice email content: `dashboard/views.py` → `email_invoice()`
- Invoice PDF design: `invoices/pdf.py` → `generate_invoice_pdf()`
- OTP SMS gateway integration (abhi console print hai): `accounts/services.py` → `generate_and_send_otp()`
- Wallet redeemable items: dashboard → "Wallet Items" se add/edit karo, koi bhi price-point set kar sakte ho
- Reward expiry days (default 60): dashboard → "Reward Settings" se admin khud badal sakta hai
- Cash denominations list (2000/500/200/100/50/20/10): `dashboard/views.py` → `mark_bill_paid()` → `DENOMINATIONS`
- Menu add-ons/extras: dashboard → "Manage Add-ons" — add any customization, set its price, pick which items it applies to
- Session/login persistence duration (default 1 saal): `config/settings.py` → `SESSION_COOKIE_AGE`
- Excel report columns: `dashboard/excel_export.py` → `generate_orders_excel()`
- Food photo filter effect: `gallery/filters.py` → `apply_artistic_filter()`
- Menu categories/items: dashboard se ya Django admin se manage karo
- Email notifications abhi add nahi hain — chaho to Django's `send_mail` se easily add ho jayenge.

## Note on "Ghibli-style" photo filters

Photo filter feature me **specific studio ka copyrighted art style (jaise "Ghibli-style")
replicate karna implement nahi kiya gaya hai** — yeh copyright infringement hoga chahe free
API use ho ya paid. Iski jagah ek generic, non-infringing "warm/painterly" filter use kiya
gaya hai (`gallery/filters.py`), jise aap kisi bhi doosre legal/licensed filter ya apne khud
ke trained model se replace kar sakte ho.
