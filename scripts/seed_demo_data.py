#!/usr/bin/env python3
"""
Seed demo data for sales/demo scenarios.
Safe to run multiple times - checks for existing data.
"""
import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.auto_reply import AutoReply
from app.models.channel import Channel
from app.models.filter import Filter
from app.models.user import User
from app.models.workspace import Workspace


async def seed_demo():
    """Seed safe demo data for commercial presentation."""
    async with AsyncSessionLocal() as session:
        # Find first user (owner)
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("❌ No user found. Create a user first via /api/v1/auth/register")
            return

        print(f"✓ Found user: {user.phone}")

        # Find first workspace
        result = await session.execute(
            select(Workspace).where(Workspace.owner_id == user.id).limit(1)
        )
        workspace = result.scalar_one_or_none()
        if not workspace:
            print("❌ No workspace found. Create one via API or admin panel.")
            return

        print(f"✓ Found workspace: {workspace.name} (ID: {workspace.id})")

        # Find first channel
        result = await session.execute(
            select(Channel).where(Channel.workspace_id == workspace.id).limit(1)
        )
        channel = result.scalar_one_or_none()
        if not channel:
            print("❌ No channel found. Create one via API or admin panel.")
            return

        print(f"✓ Found channel: {channel.name} (ID: {channel.id})")

        # Seed auto-replies (safe demo scenarios)
        demo_replies = [
            {
                "trigger_text": "قیمت",
                "reply_text": "📋 لیست قیمت محصولات:\n\n• پکیج پایه: ۵۰۰ هزار تومان\n• پکیج حرفه‌ای: ۱ میلیون تومان\n• پکیج سازمانی: تماس بگیرید\n\nبرای سفارش با پشتیبانی تماس بگیرید.",
                "match_type": "contains",
            },
            {
                "trigger_text": "ساعت کاری",
                "reply_text": "🕐 ساعت کاری پشتیبانی:\n\nشنبه تا چهارشنبه: ۹ صبح تا ۶ عصر\nپنج‌شنبه: ۹ صبح تا ۱ ظهر\n\nبرای تماس: 09001602030",
                "match_type": "contains",
            },
            {
                "trigger_text": "راهنما",
                "reply_text": "📚 راهنمای سریع:\n\n• برای دیدن قیمت‌ها: قیمت\n• برای ساعت کاری: ساعت کاری\n• برای تماس: پشتیبانی\n• برای لیست کانال‌ها: کانال‌ها",
                "match_type": "contains",
            },
            {
                "trigger_text": "پشتیبانی",
                "reply_text": "☎️ تماس با پشتیبانی:\n\nتلفن: 09001602030\nایمیل: alirezasafaeisystems@gmail.com\nتلگرام: @asdevsystems\n\nپاسخگویی در ساعات اداری",
                "match_type": "contains",
            },
        ]

        added_replies = 0
        for reply_data in demo_replies:
            # Check if exists
            result = await session.execute(
                select(AutoReply).where(
                    AutoReply.channel_id == channel.id,
                    AutoReply.trigger_text == reply_data["trigger_text"],
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                auto_reply = AutoReply(
                    channel_id=channel.id,
                    trigger_text=reply_data["trigger_text"],
                    reply_text=reply_data["reply_text"],
                    match_type=reply_data["match_type"],
                    is_active=True,
                )
                session.add(auto_reply)
                added_replies += 1

        await session.commit()
        print(f"✓ Added {added_replies} auto-reply rules")

        # Seed filters (safe demo scenarios)
        demo_filters = [
            {
                "pattern": "spam",
                "action": "warn",
                "reason": "احتمال اسپم",
            },
            {
                "pattern": "تبلیغ",
                "action": "warn",
                "reason": "تبلیغات غیرمجاز",
            },
        ]

        added_filters = 0
        for filter_data in demo_filters:
            result = await session.execute(
                select(Filter).where(
                    Filter.channel_id == channel.id,
                    Filter.pattern == filter_data["pattern"],
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                filter_rule = Filter(
                    channel_id=channel.id,
                    pattern=filter_data["pattern"],
                    match_type="contains",
                    action=filter_data["action"],
                    reason=filter_data["reason"],
                    is_active=True,
                )
                session.add(filter_rule)
                added_filters += 1

        await session.commit()
        print(f"✓ Added {added_filters} filter rules")

        print("\n✅ Demo data seeded successfully!")
        print(f"\nWorkspace ID: {workspace.id}")
        print(f"Channel ID: {channel.id}")
        print("\nYou can now:")
        print("1. Test auto-replies by sending messages with: قیمت, ساعت کاری, راهنما, پشتیبانی")
        print("2. View filters in admin panel")
        print("3. Create scheduled posts via admin panel")


if __name__ == "__main__":
    print("🌱 Seeding demo data for A05 Rubika Bot SaaS...\n")
    asyncio.run(seed_demo())
    print("\n✓ Done")
