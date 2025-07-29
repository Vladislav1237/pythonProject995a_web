# CalcNest

CalcNest is a web platform providing a catalog of online calculators for various domains:
- Mathematics
- Construction
- Medicine
- Finance

## Architecture

- Frontend: **Nuxt.js** (Vue 3) — SSR enabled
- Backend: **Laravel 11** (PHP 8+) — REST API
- Database: **PostgreSQL**
- Automatic unit tests for each formula
- API documentation via Swagger or Laravel API Resources

## Features

1. Main page with calculator categories
2. Individual calculator pages with input form, description, and results
3. API endpoints for each calculator:
   - **Input**: parameters
   - **Output**: result, formula
4. SEO-friendly URLs: `/calc/bmi`, `/calc/concrete-volume`, etc.
5. Admin panel:
   - Create/edit calculators
   - Categories management
   - Usage statistics
6. Calculator search
7. API subscription model:
   - User registration / login
   - API key generation
   - Rate limiting
   - Payment gateway integration (Stripe, etc.)
8. UI:
   - Minimalistic, responsive design
   - Dark theme support
   - SEO-optimized titles, descriptions, and results

## Monetization

- Free website access
- Paid API subscription
- Future ad placements

## Testing

- Unit tests for formula correctness
- Integration tests for API endpoints
- E2E tests for UI calculator flows

## Project Structure

```
/home/engine/project
│
├── backend/       # Laravel 11 REST API
├── frontend/      # Nuxt.js (Vue 3) SSR
└── .gitignore     # Git ignore rules
```

## Getting Started

### Backend

1. Navigate to `backend/` directory
2. Install PHP dependencies:
   ```bash
   composer install
   ```
3. Copy `.env.example` to `.env` and configure your database credentials
4. Run migrations:
   ```bash
   php artisan migrate
   ```
5. Serve the application:
   ```bash
   php artisan serve
   ```

### Frontend

1. Navigate to `frontend/` directory
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file and configure API base URL:
   ```env
   API_URL=http://localhost:8000/api
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

## CI/CD

GitHub Actions workflows will automate tests, build, and deployment for both frontend and backend.
