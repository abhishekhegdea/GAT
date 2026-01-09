# Pre-Deployment Checklist

Complete this checklist before deploying to production.

## Firebase Project Setup
- [ ] Firebase project created
- [ ] Firestore Database enabled in production mode
- [ ] Cloud Storage enabled
- [ ] Service account JSON downloaded and saved as `firebase-credentials.json`
- [ ] Project ID noted
- [ ] Storage bucket URL noted

## Code & Configuration
- [ ] `.env` file created with all required values
- [ ] `.env` added to `.gitignore`
- [ ] `firebase-credentials.json` added to `.gitignore`
- [ ] All face recognition code removed ✅
- [ ] `config.py` updated with production settings
- [ ] `FLASK_ENV=production` set in `.env`
- [ ] Strong SECRET_KEY and JWT_SECRET_KEY set (min 32 chars)

## Database
- [ ] Bootstrap script executed successfully
- [ ] All 8 Firestore collections created:
  - [ ] users
  - [ ] classes
  - [ ] enrollments
  - [ ] attendance
  - [ ] devices
  - [ ] audit_logs
  - [ ] blocked_ips
  - [ ] system_settings
- [ ] 6 System settings created with correct values
- [ ] Default admin user created
- [ ] Test users created and verified

## Security
- [ ] Firestore security rules updated and published
- [ ] Cloud Storage security rules updated and published
- [ ] CORS configured for production domain only
- [ ] SESSION_COOKIE_SECURE = True
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SESSION_COOKIE_SAMESITE = Strict
- [ ] Default admin password changed
- [ ] No credentials in code or git history

## API Testing
- [ ] Health check endpoint working: `GET /api/health`
- [ ] Authentication endpoints tested
- [ ] Student attendance endpoints tested
- [ ] Teacher endpoints tested
- [ ] Admin endpoints tested
- [ ] Error handling verified
- [ ] Rate limiting working
- [ ] CORS working correctly

## Frontend
- [ ] `.env.production` created with correct API URL
- [ ] Firebase config in frontend updated
- [ ] API calls use production endpoint
- [ ] Build tested: `npm run build`
- [ ] Production build artifacts generated

## Deployment Target
- [ ] Deployment platform selected (Cloud Run, Heroku, etc.)
- [ ] Environment variables configured on platform
- [ ] Dockerfile created (if needed)
- [ ] `.dockerignore` created (if needed)
- [ ] Dependencies pinned in `requirements.txt`
- [ ] Python version specified (3.9+)

## Monitoring & Logging
- [ ] Logging configured
- [ ] Error tracking enabled
- [ ] Uptime monitoring configured
- [ ] Database backups configured
- [ ] Alert notifications set up

## Documentation
- [ ] Deployment documentation updated
- [ ] Environment variables documented
- [ ] API documentation complete
- [ ] Known issues documented
- [ ] Rollback procedure documented

## Final Review
- [ ] Code reviewed for security issues
- [ ] No sensitive data in logs
- [ ] Performance testing completed
- [ ] Load testing completed
- [ ] All tests passing
- [ ] README updated with deployment info

## Post-Deployment
- [ ] Deployment verified and accessible
- [ ] Smoke tests passed
- [ ] Monitoring alerts working
- [ ] Database backups running
- [ ] Team notified
- [ ] Documentation links shared

---

## Deployment URLs

After deployment, update these with actual values:

- **API Base URL**: `https://your-api-domain.com/api`
- **Frontend URL**: `https://your-frontend-domain.com`
- **Admin Console**: `https://console.firebase.google.com`

## Rollback Plan

If deployment fails:
1. Identify the issue
2. Fix the problem
3. Re-deploy (automated or manual)
4. Verify all systems operational
5. Document incident in runbook

## Common Issues

**Issue**: Firestore connection fails
- **Solution**: Check FIREBASE_CREDENTIALS path and FIREBASE_PROJECT_ID

**Issue**: CORS errors
- **Solution**: Update CORS_ORIGINS in .env to match frontend domain

**Issue**: 401 Unauthorized errors
- **Solution**: Check JWT_SECRET_KEY is consistent between requests

**Issue**: Collections missing
- **Solution**: Run `python bootstrap_firestore.py` again

**Issue**: Performance degradation
- **Solution**: Create composite indexes (see deployment guide)

---

**Deployed Date**: _________________
**Deployed By**: _________________
**Version**: _________________
**Notes**: _________________
