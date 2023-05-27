# Design
Planning and research for product design.

# Core
Core design principles:
- Focus on speech.

# Plugins
Plugin system allows for multiple teaching modules, each with their own target.

## Plugin system
- Some plugins are for "sub-games" e.g. ways of structuring lessons
- These sub-games are matrixed with curriculum modules, so for example "use 'color' module with the 'use it in a
  sentence' sub-game"

## Ideas for plugins
- "Try to use these vocab words in your conversation"
    - MVP: toss in some colors, check that the user used them corectly.
- "Read this summary of a news article and answer some questions"

## Curriculum
- Curriculum sketched in `planning/design_a_course.txt`
    - beginner 12 week course
    - basic vocabulary and grammar modules

# Privacy
"""
The only user data I collect is your conversation transcripts. Voice recordings are deleted at the end of each session.
Transcripts are kept to help you track your progress and hone in on problem areas. If you want, you can request that I
delete all your user data, including the transcripts of your conversations - you can download a copy before you submit
the deletion request if you want, and then I'll delete them en toto.

Having said this, I can't guarantee the same for OpenAI, who provide the conversational AI that powers Moshi. They will
keep both your voice recordings and conversational transcripts. The same goes for Google, who uses tracking cookies to
serve you targeted ads - they'll of course keep that data.
"""

# Monetization
- Free tier uses text-davinci-003, requires the user to get their own API key
- Ads
