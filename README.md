## Description

This project is a collection of apps for managing and processing RSS feeds, grouping sources, and sending personalized newsletters to subscribed users.

### Features
- **Authentication (accounts app)**: Simple token-based authentication for users.
- **RSS Client (rss_client app)**: Fetches feeds from sources that the user has added. It generates categories and tags for each feed using GPT.
- **Source Grouping (group app)**: Groups sources into a single group for better organization.
- **Background Tasks**: Fetches RSS feeds, generates newsletters, and sends them to subscribers via email. Tasks are scheduled to run at specified intervals.
