### RastaBot for the Irie Army discord server

### About
RastaBot is a custom bot created for the Irie Army discord server. This bot's main objective is to help the users and moderators of the Irie Army discord better enjoy their time in the community. RastaBot is not intended as a moderator replacement.

### Features Overview
The RastaBot supports requests (from users) and commands (from BotManagers)
 ## Requests
    - $help: This request sends a DM containing all possible requests from a user
    - $links: Sends a user a DM with links to Irie Genetics beans, Grow From Your Heart podcast locations and other important links
    - $rules: DM the user the current rules message
    - $waffle_rules/waffles_rules: Sends a user a DM with the rules of waffles
    - $action_rules/actions_rules: Sends a user a DM with the rules of actions
    - $about: Shows information about RastaBot wherever the request is issued
    - Monitors user messages in all channels the bot is in. Tags users and responds when a custom list of bad words is mentioned.
 ## Commands
    - !get_season: Shows the current welcome message season
    - !set_season [season_name]: Sets the current season to a known season (prevents typos)
    - !new_season [season_name]: Creates a new season
    - !new_welcome_message [season_name] [welcome message formatted]: Creates a new welcome message in season_name with formatting. Use {} to indicate the user's name, mentioned. 
    - !list_welcome_messages: Lists welcome messages in the current season. To see other seasons, !set_season and !list_welcome_messages
    - !delete_welcome_message [index]: Deletes welcome message from current season at index
    - !clear_welcomed_members: Completely removes every member from a list of known members.
    - !new_role_message_id [id]: Sets which message the bot should monitor for the @Irie Army role reaction
    - !new_rules_message_id [id]: Sets which message the bot should copy when sending the rules
    - !new_actions_message_id [id]: Sets which message the bot should copy when sending the actions/waffle rules
    - !new_links_message_id [id]: Sets which message the bot should copy when sending links.
    - !db_update [db_key] [db_value]: Put a key:value pair in the db manually
    - !db_delete [db_ley]: Delete a key entirely from the db. Requires confirmation in the console (Trolan)
    - !add_bad_word [bad word or phrase]: Adds a new bad word or phrase to the list
    - !list_bad_words: Lists all current bad words
    - !delete_bad_word [bad word or phrase]: Deletes a bad word or phrase from the list
    - !new_reaction_message [msg_id]: Tells the bot to start watching this message for reactions
    - !delete_reaction_message [msg_id]: Tells the bot to no longer watch this message AND DELETES ALL ASSOCIATED EMOJIS AND ROLES
    - !new_role_reaction [msg_id] [emoji] [role_id]: Tells the bot to assign/remove role_id when the emoji reaction is a added/removed from msg_id
    - !delete_role_reaction [msg_id] [emoji]: Deletes the emoji:role_id pairing from the msg_id - the bot no longer assigns that role for that emoji
    - !list_role_reaction [msg_id]: Lists all available reactions for the given msg_id
    
    
>This bot is free to the Irie Army but does have a low cloud operating cost. If you want to help me out, or buy me a beer: 
>  
>[<img src="https://img.buymeacoffee.com/api/?url=aHR0cHM6Ly9pbWcuYnV5bWVhY29mZmVlLmNvbS9hcGkvP25hbWU9VHJldm9yK01hdGhpc2VuJnNpemU9MzAwJmJnLWltYWdlPWJtYyZiYWNrZ3JvdW5kPUZGODEzRg==&creator=Trevor+Mathisen&is_creating=building%20more%20code%20every%20day&design_code=1&design_color=%23FF813F&slug=trolan" width="350"/>](https://www.buymeacoffee.com/trolan)
