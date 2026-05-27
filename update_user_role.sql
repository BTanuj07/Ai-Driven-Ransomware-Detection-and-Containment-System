-- Update User Role in Supabase
-- Run this in Supabase SQL Editor

-- First, check current users and their roles
SELECT 
    id,
    email,
    raw_user_meta_data->>'role' as current_role,
    created_at
FROM auth.users
ORDER BY created_at DESC;

-- ============================================
-- UPDATE USER ROLE TO INCIDENT RESPONDER
-- ============================================
-- Replace 'user@example.com' with the actual email address

UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
    COALESCE(raw_user_meta_data, '{}'::jsonb),
    '{role}',
    '"responder"'
)
WHERE email = 'user@example.com';  -- CHANGE THIS EMAIL

-- ============================================
-- AVAILABLE ROLES:
-- ============================================
-- 'superadmin' - Full system access
-- 'analyst'    - SOC Analyst (monitoring + investigation)
-- 'responder'  - Incident Responder (analyst + action execution)
-- 'viewer'     - Read-only access

-- ============================================
-- EXAMPLES FOR OTHER ROLES:
-- ============================================

-- Set user as SOC Analyst:
-- UPDATE auth.users
-- SET raw_user_meta_data = jsonb_set(
--     COALESCE(raw_user_meta_data, '{}'::jsonb),
--     '{role}',
--     '"analyst"'
-- )
-- WHERE email = 'analyst@example.com';

-- Set user as Superadmin:
-- UPDATE auth.users
-- SET raw_user_meta_data = jsonb_set(
--     COALESCE(raw_user_meta_data, '{}'::jsonb),
--     '{role}',
--     '"superadmin"'
-- )
-- WHERE email = 'admin@example.com';

-- Set user as Viewer:
-- UPDATE auth.users
-- SET raw_user_meta_data = jsonb_set(
--     COALESCE(raw_user_meta_data, '{}'::jsonb),
--     '{role}',
--     '"viewer"'
-- )
-- WHERE email = 'viewer@example.com';

-- ============================================
-- VERIFY THE UPDATE:
-- ============================================
SELECT 
    id,
    email,
    raw_user_meta_data->>'role' as updated_role,
    raw_user_meta_data
FROM auth.users
WHERE email = 'user@example.com';  -- CHANGE THIS EMAIL
