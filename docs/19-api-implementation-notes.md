# API Implementation Notes

## پیشنهاد Route Grouping
```text
/api/v1/auth/*
/api/v1/workspaces/*
/api/v1/workspaces/{workspace_id}/channels/*
/api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/*
/api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/*
/api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/*
/api/v1/workspaces/{workspace_id}/reports/*
/api/v1/webhooks/rubika/*

---

## Middlewareهای پیشنهادی
- Request ID middleware
- Auth middleware
- Workspace access middleware
- Validation middleware
- Error handler middleware
- Rate limiter
- Logging middleware

---

## سرویس‌های اصلی
- AuthService
- WorkspaceService
- ChannelService
- ScheduledPostService
- SchedulerWorkerService
- AutoReplyService
- FilterService
- ReportingService
- WebhookService

---

## نکات مهم پیاده‌سازی

### 1. Ownership Check
هر بار که `workspace_id`, `channel_id`, `post_id`, `rule_id` دریافت می‌شود:
- باید بررسی شود که منبع متعلق به همان کاربر/Workspace است

### 2. Transaction
برای عملیات‌های مهم از transaction استفاده شود:
- ایجاد Rule + Keywords
- ایجاد Post + Activity Log
- ارسال Post + Post Log + Activity Log

### 3. Idempotency
در پردازش webhook:
- اگر event تکراری رسید، دوباره پردازش نشود

### 4. Soft Delete
در پیاده‌سازی واقعی بهتر است:
- `deleted_at`
- یا `status = deleted`

### 5. Audit Logs
برای عملیات مدیریتی مهم:
- ثبت در `activity_logs`

---

## ترتیب پیشنهادی پیاده‌سازی API
1. Auth
2. Workspaces
3. Channels
4. Scheduled Posts
5. Auto Replies
6. Filters
7. Reports
8. Webhooks

---

## Minimum Test Cases
- ثبت کاربر
- ورود کاربر
- ساخت Workspace
- افزودن Channel
- ساخت Scheduled Post
- ویرایش Scheduled Post
- ساخت Auto Reply Rule
- ساخت Filter Rule
- گزارش Summary
- دریافت webhook پیام


---
