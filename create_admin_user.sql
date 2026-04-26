-- ============================================
-- ARCS Dashboard - Create Admin User
-- ============================================
-- Run this SQL in Supabase SQL Editor
-- Project: hsbcjonzbnwjnftfohyk
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================
-- CREATE ADMIN USER: tanuj077777@gmail.com
-- ============================================
-- IMPORTANT: Change the password below!
-- ============================================

INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_user_meta_data,
  raw_app_meta_data,
  created_at,
  updated_at,
  confirmation_token,
  recovery_token,
  email_change_token_new,
  email_change
)
VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'tanuj077777@gmail.com',
  crypt('Admin@123', gen_salt('bf')),  -- ⚠️ CHANGE THIS PASSWORD!
  now(),
  '{"role": "admin", "username": "tanuj", "full_name": "Tanuj"}'::jsonb,
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  now(),
  now(),
  '',
  '',
  '',
  ''
)
ON CONFLICT (email) 
DO UPDATE SET 
  raw_user_meta_data = '{"role": "admin", "username": "tanuj", "full_name": "Tanuj"}'::jsonb,
  email_confirmed_at = now();

-- ============================================
-- CREATE TEST USERS (Optional)
-- ============================================

-- Analyst User
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_user_meta_data,
  raw_app_meta_data,
  created_at,
  updated_at,
  confirmation_token,
  recovery_token,
  email_change_token_new,
  email_change
)
VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'analyst@arcs.local',
  crypt('analyst123', gen_salt('bf')),
  now(),
  '{"role": "analyst", "username": "analyst", "full_name": "Security Analyst"}'::jsonb,
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  now(),
  now(),
  '',
  '',
  '',
  ''
)
ON CONFLICT (email) DO NOTHING;

-- Viewer User
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_user_meta_data,
  raw_app_meta_data,
  created_at,
  updated_at,
  confirmation_token,
  recovery_token,
  email_change_token_new,
  email_change
)
VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'viewer@arcs.local',
  crypt('viewer123', gen_salt('bf')),
  now(),
  '{"role": "viewer", "username": "viewer", "full_name": "Security Viewer"}'::jsonb,
  '{"provider": "email", "providers": ["email"]}'::jsonb,
  now(),
  now(),
  '',
  '',
  '',
  ''
)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- VERIFY USERS CREATED
-- ============================================

SELECT 
  email,
  raw_user_meta_data->>'role' as role,
  raw_user_meta_data->>'username' as username,
  email_confirmed_at,
  created_at
FROM auth.users
WHERE email IN ('tanuj077777@gmail.com', 'analyst@arcs.local', 'viewer@arcs.local')
ORDER BY 
  CASE raw_user_meta_data->>'role'
    WHEN 'admin' THEN 1
    WHEN 'analyst' THEN 2
    WHEN 'viewer' THEN 3
  END;

-- ============================================
-- EXPECTED OUTPUT:
-- ============================================
-- email                    | role    | username | email_confirmed_at | created_at
-- -------------------------|---------|----------|--------------------|-----------
-- tanuj077777@gmail.com    | admin   | tanuj    | 2026-04-22...      | 2026-04-22...
-- analyst@arcs.local       | analyst | analyst  | 2026-04-22...      | 2026-04-22...
-- viewer@arcs.local        | viewer  | viewer   | 2026-04-22...      | 2026-04-22...
-- ============================================

-- ============================================
-- LOGIN CREDENTIALS
-- ============================================
-- Admin:   tanuj077777@gmail.com / Admin@123 (change this!)
-- Analyst: analyst@arcs.local / analyst123
-- Viewer:  viewer@arcs.local / viewer123
-- ============================================
