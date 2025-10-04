# capybara-parkour
An Arcade Game of a Capybara doing Parkour

# project structure

The game runs on a Raspberry PI with a Nextion display connected to GPIO.

This is the structure of the project:
-src/display: Nextion project files
-src/engine: Python project with the game engine, reading/writing to Nextion interface to control the display pages, variables and animations
-src/script: Python utility scripts to upload the Nextion project to the display