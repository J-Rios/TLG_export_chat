# TLG_export_chat

## Description:

Python script that use the Telegram Client API to get all chat messages and export them to a file.

-------------------------------------------------------------------------------------------------------------------------

## How to use:

1 - First, you need a Telegram Client-API ID and Application Hash. You can get them by login and creating a new "App" in:
https://my.telegram.org

2 - Next, you have to set them ("API_ID", "API_HASH" and "PHONE_NUM") in "firstrun.py" file.

3 - Then, you have to execute "firstrun.py" to request a "LOGIN_CODE" that will be sent and can be read from Telegram Android/IOS/Desktop:
python3 firstrun.py

4 - At last, you have to set yours "API_ID", "API_HASH", "PHONE_NUM", "LOGIN_CODE" and "CHAT_LINK" in "tlg_exportchat.py" file.

5 - Now, you are free to execute "tlg_exportchat.py" file to export the "CHAT_LINK" chat data:
python3 tlg_exportchat.py

-------------------------------------------------------------------------------------------------------------------------

## Notes:

- Once you get a LOGIN_CODE, you does not need to do steps 2 and 3 of "How to use" section again.

- This tool must be use from Python 3 (no Python 2 support).

- The duration of the export process goes from minutes to hours depending on messages number of a chat.
