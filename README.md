# GenomeWiz
Expert crowdsourcing of structural-variant (SV) labels to build ML models for SV callers

### Authentication

GenomeWiz uses **Google Sign-In** for identity and issues its own **JWT** for API access.

1. Create OAuth 2.0 Client ID (Web) in Google Cloud Console.
2. Authorized redirect URI: `http://localhost:8000/auth/callback`
3. Set env vars in `.env`:
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_CALLBACK_URL`
   - `SESSION_SECRET`, `JWT_SECRET`
   - Optional: `ALLOWED_GSUITE_DOMAIN=yourlab.org`
4. Start the app and open `http://localhost:8000/auth/login`.
5. On success, the app redirects to `/auth/signed-in#token=<JWT>` (for SPA) and stores a minimal server session. Use the `Authorization: Bearer <JWT>` header for API calls.

**Roles**
- First user becomes `admin` automatically (dev convenience).
- Admins can grant roles by inserting into `user_roles` (admin UI coming later).
- Protected endpoints require `curator` or `admin`.
