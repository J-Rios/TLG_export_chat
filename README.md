# TLG_export_chat

## Description:

Python script that use the Telegram Client API to get all chat messages and export them to a file.

-------------------------------------------------------------------------------------------------------------------------

## How to use:

1 - First, you need a Telegram Client-API ID and Application Hash. You can get them by login and creating a new "App" in:
https://my.telegram.org

2 - Next, you have to set "API_ID", "API_HASH", "PHONE_NUM" and "CHAT_LINK" (chat that you want to export the data) in "tlg_exportchat.py" file.

3 - Then, you are free to execute "tlg_exportchat.py" file to export the chat data from the "CHAT_LINK" provided:
python3 tlg_exportchat.py

-------------------------------------------------------------------------------------------------------------------------

## Notes:

- The first time that you run the script, it requests a "Sign-in Code", to Telegram client API service, and wait for the user to input that code.

- The "Sign-in Code" will be sent by "Telegram Service Notifications" account, and it can be read from any Telegram Android/IOS/Desktop App.

- Once you insert the "Sign-in Code" and the connection is successfully established, the sign-in validation is stored in a file named "Session.session".

- The "Session.session" file is used in next scripts runs (logins attempts), so it wont request a Sign-in Code again.

- If you still have problems for sign in when using the correct received code, delete the "Session.session" file and try again.

- This script must be use from Python 3 (no Python 2 support).

- The duration of the export process goes from minutes to hours depending on the number of messages that the chat has.
