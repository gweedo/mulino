# Admin access decided by a `menu_manager` role claim

Admin access is decided by the `app_metadata.role = "menu_manager"` claim in the Supabase JWT, not by a local owners table. The role is named after the capability rather than the person so future staff are added by granting the role, with no schema change. `user_metadata` is never used for access decisions because users can edit it themselves; `app_metadata` is admin-only.
