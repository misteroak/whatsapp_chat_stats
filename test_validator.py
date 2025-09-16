#!/usr/bin/env python3
"""
Test script to verify validator and parser work with the provided WhatsApp chat sample
"""

from utils.validators import is_whatsapp_chat_format, validate_uploaded_file
from utils.chat_parser import parse_whatsapp_file

# Sample WhatsApp chat content (anonymized for testing)
sample_chat = """[01/02/2024, 7:59:39 AM] Alice Smith: ‎Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.
[01/02/2024, 7:59:39 AM] Alice Smith: ‎‎‎You use a default timer for disappearing messages in new chats. ‎New messages will disappear from this chat ‎24 hours after they're sent, except when kept. ‎Tap to update your own default timer.
[01/02/2024, 7:59:39 AM] Alice Smith: ‎‎Disappearing messages were turned off. ‎Tap to change.
‎[01/02/2024, 7:58:10 AM] Alice Smith: ‎image omitted
[01/02/2024, 7:59:53 AM] Bob Jones: What, nooo
[01/02/2024, 8:00:11 AM] Bob Jones: Go do pilates, clean that later
[01/02/2024, 8:01:06 AM] Alice Smith: But it might stain the longer it's on there
[01/02/2024, 8:02:42 AM] Bob Jones: Yeah you'e right
[01/02/2024, 8:03:34 AM] Bob Jones: Hope you get it off
[01/02/2024, 8:14:42 AM] Alice Smith: Well, I listened to you and went to Pilates. I spray some detergent on it. Gonna let it sit and hope that it comes out
[01/02/2024, 8:19:06 AM] Bob Jones: Good 💪 Your mind and body are more important
[01/02/2024, 9:45:31 AM] Bob Jones: Landed
[01/02/2024, 9:48:20 AM] Alice Smith: Still at the gym trying to get some cardio in
[01/02/2024, 12:04:57 PM] Bob Jones: The interenet in this country is sooo slow
[01/02/2024, 12:34:31 PM] Alice Smith: Miss you…
[01/02/2024, 1:59:19 PM] Bob Jones: Me too. Very much.
[01/02/2024, 2:55:45 PM] Bob Jones: Wordle 784 4/6

⬜🟨⬜⬜⬜
⬜⬜⬜🟨🟨
⬜⬜🟩🟩⬜
🟩🟩🟩🟩🟩"""


def test_validator():
    """Test the validator with the sample chat"""
    print("Testing validator...")

    # Test format validation
    is_valid, error_msg = is_whatsapp_chat_format(sample_chat)
    print(f"Format validation: {'PASS' if is_valid else 'FAIL'}")
    if error_msg:
        print(f"Error: {error_msg}")

    # Test full file validation
    content_bytes = sample_chat.encode('utf-8')
    is_valid_file, errors, file_info = validate_uploaded_file(
        "test_chat.txt", content_bytes)
    print(f"File validation: {'PASS' if is_valid_file else 'FAIL'}")
    if errors:
        print(f"Errors: {errors}")

    print(f"File info: {file_info}")
    print()


def test_parser():
    """Test the parser with the sample chat"""
    print("Testing parser...")

    try:
        messages, stats = parse_whatsapp_file(sample_chat, "test_chat.txt")
        print(f"Parsed {len(messages)} messages")
        print(f"Statistics: {stats}")

        print("\nFirst few parsed messages:")
        for i, msg in enumerate(messages[:5]):
            print(
                f"{i+1}. [{msg.timestamp}] {msg.sender}: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")

        print(f"\nMessage breakdown:")
        print(f"- Total messages: {len(messages)}")
        print(f"- Unique senders: {len(set(msg.sender for msg in messages))}")
        print(
            f"- Media messages: {sum(1 for msg in messages if msg.is_media)}")

    except Exception as e:
        print(f"Parser failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing WhatsApp Chat Validator and Parser")
    print("=" * 50)

    test_validator()
    test_parser()

    print("Test completed!")
