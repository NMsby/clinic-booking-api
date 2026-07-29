# CLAUDE.md

This file is read by Claude Code at the start of every session and after every context compaction. If context has been compacted, stop and tell Nelson to start a fresh session rather than continuing.

## Project

Clinic Booking API -- Savannah Informatics Backend Developer Take-Home Assessment        
Repository: https://github.com/NMsby/clinic-booking-api             
Developer: Nelson Masbayi Muyodi          
GitHub: NMsby           

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Docker
- GCP Cloud Run
- GitHub Actions

## Running Python commands

The project's dependencies are installed inside a virtual environment in WSL Ubuntu-22.04, at /home/nelson/projects/clinic-booking-api/.venv, not system wide. A bare python3, pip, pytest, alembic, or uvicorn command run from this shell resolves to a Windows stub rather than WSL. Even a plain wsl python3 reaches WSL's system Python rather than this project's virtual environment.

Two patterns are confirmed working from this shell for reaching the venv interpreter directly.

Pattern 1: MSYS_NO_PATHCONV=1 wsl /home/nelson/projects/clinic-booking-api/.venv/bin/python

The MSYS_NO_PATHCONV=1 prefix prevents Git Bash from converting the Unix path to a Windows path before passing it to wsl. Without it, wsl receives a path like C:/Program Files/Git/home/nelson/projects/clinic-booking-api/.venv/bin/python and fails with: No such file or directory. Always prefix MSYS_NO_PATHCONV=1 when using this pattern.

Pattern 2: wsl bash -c '/home/nelson/projects/clinic-booking-api/.venv/bin/python -c "..."'

Wrapping the command in wsl bash -c with single quotes passes the path to WSL's bash without Git Bash touching it. This pattern is also confirmed working and is more natural for multi-argument commands such as running a module.

Use either pattern for all venv commands: pytest, uvicorn, pip install, alembic. If a command returns a Windows path such as C:/Program Files/Git/home/... inside a No such file or directory error, that is the specific symptom that Git Bash converted the path before wsl received it. Apply pattern 1 or pattern 2 to fix it.

## Absolute Rules (no exceptions)

- Never add Co-Authored-By lines to commit messages. All commits are by Nelson Masbayi Muyodi only.
- Never use em dashes in any output, documentation, code comments, or commit messages. Use commas, colons, semicolons, or periods instead.
- Never use emojis anywhere. 
- Read a file before modifying it. Always.
- Reference files by full path, never from memory.
- Never assume the current state of a file. Read it first.

## File Structure

Read /CLAUDE.md first.              
Read /README.md for system design context.              
API code is in /app/              
Tests are in /tests/            
Database models are in /app/models/           
API routes are in /app/routes/              
Business logic is in /app/services/             

## Commit Message Format

feat: description of new feature              
fix: description of bug fix               
test: description of test addition            
docs: description of documentation change           
chore: description of maintenance task            

Example: feat: add GET /doctors/{id}/availability endpoint              

## Environment Variables

Never hardcode credentials. Always use environment variables.               
See .env.example for required variables.                
Never commit .env files.            

## After Compaction

If Claude Code context has been compacted, stop immediately. Tell Nelson: "Context has been compacted. Please start a fresh Claude Code session and paste the first message from the session guide in CLAUDE.md."

Fresh session opening prompt:         
"Read /CLAUDE.md in full before doing anything else. Confirm you have read it by listing the stack and the three most important absolute rules."
