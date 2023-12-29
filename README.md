# LinkGen 

Small plugin with the aim of simplifying tag generation for documents

## Current Features

> Note: Commands can be accessed through the command palette (`Ctrl+P`)

`Generate Tags`: Command to create a tag list where all automatically generated and inserted tags will reside.
- Location of tag list in document should not matter

`Insert Tag`: Command inserting currently selected text into tag list
- Shortcut of `Ctrl+Alt+T` as alternative to command 


## Future Plans
- Generate tags command will have keyword extraction to suggest initial tags for the document 
  - Modal to select which tags to include
- Option to regenerate tags
- Add Settings menu to customize hotkeys for commands

## Installation


The following is for local testing:
1. Ensure Community Plugins setting is enabled
2. Navigate to `path-to-vault/.obsidian/plugins`
3. Clone Repo in this folder and enter repo root folder
4. Run `npm i` for first time installation
5. Run `npm run dev`
6. Enable plugin in the community plugins menu
