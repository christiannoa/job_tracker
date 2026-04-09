# AI Usage Documentation

## Tools Used

- **Claude (Anthropic)** — Primary tool used throughout the project for code generation, debugging, deployment guidance, and concept explanations
- **ChatGPT (OpenAI)** — Used for code comparison and a second opinion on certain implementations; also attempted MySQL debugging on laptop before switching to desktop

---

## Key Prompts

**Initial Build**

> "I've never built a web app before. I want to build a job application tracker. can you show me the best route based on these requirements? let's walk step by step."

> "What is the best folder structure for a Flask web application that has multiple pages and connects to MySQL?"

> "I want to understand these files and their purpose. Elaborate so I can understand and re-explain. What does each file do."

**Backend & Database**

> "Can you write a database.py file that separates all SQL queries from my Flask routes so my code stays organized?"

> "How do I store skills as a JSON array in MySQL and then read them back into Python as a list?"

> "What does @app.route actually do? How does Flask know which function to run when I visit a URL?"

> "Write all the Flask routes I need for full CRUD — create, read, update, delete — for a companies table."

**Frontend & Templates**

> "How does data get from Python into the HTML? What is {{ }} and {% %} doing in the template files?"

> "Build a base HTML template with a sidebar navigation that all my other pages can inherit from using Jinja2."

> "How do I pass data from a Flask route into an HTML template and loop through it to build a table?"

> "Build an add and edit form in HTML that works for both creating a new record and updating an existing one using the same template."

**Features**

> "Build a job match feature where a user enters their skills and the app ranks all jobs by how closely the requirements match."

> "How do I add flash messages in Flask so the user sees a success or error banner after submitting a form?"

> "Add a confirmation modal that appears when a user clicks delete so they have to confirm before the record is removed."

**Environment & Setup**

> "What is a .env file and why can't I just put my database password directly in app.py?"

> "How do I use a .env file in Flask to store my database credentials so I never hardcode passwords in my code?"

> "Write a schema.sql file with sample data so anyone who clones my project can set up the database in one step."

**Deployment**

> "I got ERROR 1045 (28000): Access denied for user 'root'@'localhost'"

**Personal Features**

> "I want to add my own spin on this. Walk me through some ideas — something we can do relatively quickly to add some of my own personality to it."

> "I want a motivational quote banner at the top of the dashboard with real quotes from people I actually look up to — Jordan, Kobe, Mayweather, Cuban, Jobs, Ali."

> "Build a Win Wall section at the bottom of the dashboard that shows only my Interview and Offer applications as achievement cards so I can see my progress visually."

> "How do I make the quote rotate randomly every time the page loads without using JavaScript or a database?"

> "What should the Win Wall look like when it's empty — should it be hidden or should it show an encouraging message?"

> "Should Offers and Interviews look the same on the Win Wall or should they be visually different so I can tell them apart at a glance?"

---

## What Worked Well

- **Full project scaffold** — Worked diligently with Claude and ChatGPT to generate 15+ files (app.py, database.py, schema.sql, 10 HTML templates, CSS) with a consistent structure and design
- **Dark theme UI** — The CSS and design system was generated with a professional dark aesthetic, custom fonts, and component styles without any manual styling
- **Debugging guidance** — Claude walked through every error step by step, from MySQL access denied errors to Jinja2 syntax issues to Mac socket connection problems
- **Explanations** — Claude broke down every file and key line of code in plain language, making it easy to understand and re-explain the project
- **Personal features** — worked with Claude and built both the quote banner and Win Wall cleanly into the existing codebase without breaking anything

---

## What I Modified

- **Renamed `base.html` to `main.html`** — Personal preference for naming clarity; updated all 10 templates using VS Code find and replace
- **Moved `static/` folder** — It was incorrectly nested inside `templates/`; moved it to the project root so CSS loaded correctly
- **Fixed `jobs.html` Jinja2 slice syntax** — Claude's original code used `[:4]` which Jinja2 doesn't support; replaced with `{% if loop.index <= 4 %}` pattern
- **Added `unix_socket` to `database.py`** — Required for Mac MySQL connections which use socket files instead of TCP
- **Updated `DB_HOST` from `127.0.0.1` to `localhost`** — Mac MySQL only accepted localhost connections, not the IP address
- **Fixed `schema.sql` contacts table** — Changed `CREATE TABLE IF NOT EXISTS` to `DROP TABLE / CREATE TABLE` to resolve column name mismatch error
- **Reset MySQL root password** — Used `--skip-grant-tables` safe mode to reset forgotten password on local machine
- **Added `get_win_wall()` to `database.py`** — New query function that joins applications, jobs, and companies to return only Interview and Offer records with full details; required adding a new function rather than reusing existing queries because the filtering and JOIN logic was specific to this feature
- **Updated `dashboard()` route in `app.py`** — Modified to import `random`, select a quote on every request using `random.choice()`, call `get_win_wall()`, and pass both into the template as new variables alongside the existing stats
- **Updated `dashboard.html`** — Added the quote banner block at the top of the content area and the Win Wall grid section at the bottom; both required new Jinja2 template logic to handle empty states gracefully
- **Added Win Wall and quote banner CSS to `style.css`** — Appended new component styles for `.quote-banner`, `.win-card`, `.win-wall-grid`, and `.win-wall-empty`; Offers styled in green, Interviews in blue to match the existing badge color system

---

## Personal Features Added

**Motivational Quote Banner**

- Added a rotating quote banner at the top of the dashboard pulling from a curated list of 20 quotes
- Quotes sourced from Michael Jordan, Kobe Bryant, Floyd Mayweather, Mark Cuban, Steve Jobs, Muhammad Ali, Wayne Gretzky, and others who built something from nothing
- Quote is selected randomly in Python using `random.choice()` on every page load — no JavaScript, no database needed
- Styled with italic serif font, blue left border, and subtle glow effect to make it stand out from the data

**Win Wall**

- Added a dedicated Win Wall section at the bottom of the dashboard
- Pulls all applications with status `Interview` or `Offer` from the database using a new `get_win_wall()` function in `database.py`
- Displays as achievement cards — green top border for Offers, blue for Interviews
- Shows job title, company, location, and salary range on each card
- When empty, shows an encouraging message: "Keep applying. Every interview and offer lands on this wall."

---

## Lessons Learned

- **Environment variables matter** — The `.env` file must be in the exact same folder as `app.py` for `python-dotenv` to read it; misplacement caused multiple "Access Denied" errors that looked like MySQL problems but were actually Python not finding the credentials
- **Mac MySQL uses sockets not TCP** — Connecting via `localhost` works but `127.0.0.1` does not on Mac without additional configuration; adding `unix_socket='/tmp/mysql.sock'` to the connector resolved this
- **Jinja2 is not Python** — Not all Python syntax works inside Jinja2 templates; slice notation `[:4]` is not supported and must be replaced with loop-based conditionals
- **Folder structure is critical for Flask** — The `static/` folder must sit at the project root level, not inside `templates/`; Flask has strict conventions for where it looks for static files
- **Always commit `.gitignore` first** — Adding `.gitignore` before any other files ensures sensitive files like `.env` are never accidentally committed
- **Separate commits tell a cleaner story** — Committing files in logical groups (backend files, templates, CSS) makes the git history easier to read and debug later
- **MySQL doesn't always start automatically** — On Mac, MySQL stops when the machine restarts or sleeps; you have to manually run `sudo /usr/local/mysql/support-files/mysql.server start` every session before running the app
- **Syntax errors are silent until runtime** — A missing comma in `database.py` after adding the `unix_socket` line didn't throw an error in VS Code but crashed the app the moment Flask tried to connect to MySQL
- **Two AI tools give different perspectives** — Using ChatGPT to compare approaches helped validate Claude's implementation and highlighted differences in how each tool structures a Flask project; Claude was more consistent across all files while ChatGPT was useful for quick second opinions
- **Ask design questions before building** — For personal features like the Win Wall and quote banner, thinking through placement, empty states, and visual differentiation before starting would have avoided back-and-forth; knowing upfront that Offers should look different from Interviews made the card design cleaner
