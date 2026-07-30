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

The reliable pattern, confirmed working on every command tried so far, including multi-argument commands with flags, is: prefix with MSYS_NO_PATHCONV=1 and invoke the virtual environment's interpreter by its full path. For example: MSYS_NO_PATHCONV=1 wsl /home/nelson/projects/clinic-booking-api/.venv/bin/python -m pytest, MSYS_NO_PATHCONV=1 wsl /home/nelson/projects/clinic-booking-api/.venv/bin/python -m pip install followed by a package name, MSYS_NO_PATHCONV=1 wsl /home/nelson/projects/clinic-booking-api/.venv/bin/python -m alembic upgrade head. Use this pattern as the default for every venv command.

An alternative pattern, wsl bash -c '...' wrapping the whole command in single quotes, has worked for simple single-argument invocations such as a bare python -c "..." check, but has also failed on multi-argument commands with flags, such as pip uninstall -y, with the same underlying symptom, a Windows path such as C:/Program Files/Git/... appearing inside a No such file or directory error. Do not rely on this pattern for pip, pytest, alembic, or uvicorn commands. Use the MSYS_NO_PATHCONV pattern above instead.

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
