-- =========================================================
-- Rubika Bot SaaS - MVP SQL Schema
-- Database: PostgreSQL
-- =========================================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    rubika_user_id VARCHAR(100) UNIQUE,
    full_name VARCHAR(150),
    username VARCHAR(100),
    phone VARCHAR(30),
    role VARCHAR(30) NOT NULL DEFAULT 'customer',
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE workspaces (
    id BIGSERIAL PRIMARY KEY,
    owner_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE workspace_members (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL DEFAULT 'admin',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE TABLE channels (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    rubika_chat_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    bot_is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    settings_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, rubika_chat_id)
);

CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    plan_name VARCHAR(50) NOT NULL DEFAULT 'free',
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    starts_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ends_at TIMESTAMP,
    max_channels INT NOT NULL DEFAULT 1,
    max_scheduled_posts INT NOT NULL DEFAULT 50,
    max_auto_reply_rules INT NOT NULL DEFAULT 10,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE scheduled_posts (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    content_type VARCHAR(30) NOT NULL DEFAULT 'text',
    text_content TEXT,
    media_url TEXT,
    media_file_id VARCHAR(200),
    caption TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'scheduled',
    sent_at TIMESTAMP,
    error_message TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE post_logs (
    id BIGSERIAL PRIMARY KEY,
    scheduled_post_id BIGINT NOT NULL REFERENCES scheduled_posts(id) ON DELETE CASCADE,
    attempt_no INT NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL,
    response_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE auto_reply_rules (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    match_type VARCHAR(30) NOT NULL DEFAULT 'contains',
    reply_text TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INT NOT NULL DEFAULT 100,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE auto_reply_keywords (
    id BIGSERIAL PRIMARY KEY,
    rule_id BIGINT NOT NULL REFERENCES auto_reply_rules(id) ON DELETE CASCADE,
    keyword VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE auto_reply_logs (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    rule_id BIGINT REFERENCES auto_reply_rules(id) ON DELETE SET NULL,
    sender_rubika_user_id VARCHAR(100),
    incoming_message TEXT,
    matched_keyword VARCHAR(200),
    reply_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE filter_rules (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    rule_type VARCHAR(30) NOT NULL,
    pattern VARCHAR(255) NOT NULL,
    action_type VARCHAR(30) NOT NULL DEFAULT 'delete_message',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE moderation_logs (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    rule_id BIGINT REFERENCES filter_rules(id) ON DELETE SET NULL,
    sender_rubika_user_id VARCHAR(100),
    message_text TEXT,
    detected_value VARCHAR(255),
    action_type VARCHAR(30) NOT NULL,
    result_status VARCHAR(30) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE activity_logs (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id BIGINT REFERENCES channels(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    meta JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scheduled_posts_status_time
ON scheduled_posts(status, scheduled_at);

CREATE INDEX idx_scheduled_posts_channel_id
ON scheduled_posts(channel_id);

CREATE INDEX idx_auto_reply_keywords_rule_id
ON auto_reply_keywords(rule_id);

CREATE INDEX idx_auto_reply_rules_channel_active_priority
ON auto_reply_rules(channel_id, is_active, priority);

CREATE INDEX idx_filter_rules_channel_active
ON filter_rules(channel_id, is_active);

CREATE INDEX idx_post_logs_post_id
ON post_logs(scheduled_post_id);

CREATE INDEX idx_auto_reply_logs_channel_id
ON auto_reply_logs(channel_id);

CREATE INDEX idx_moderation_logs_channel_id
ON moderation_logs(channel_id);

CREATE INDEX idx_activity_logs_workspace_created_at
ON activity_logs(workspace_id, created_at);
