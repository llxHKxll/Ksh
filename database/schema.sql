CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER DEFAULT 3000,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                health INTEGER DEFAULT 100,
                last_activity_time INTEGER DEFAULT 0,
                last_claimed INTEGER DEFAULT 0,
                chat_id INTEGER DEFAULT 0,
                xp_booster_expiry INTEGER DEFAULT 0  -- Add this column to track booster expiry
            );
