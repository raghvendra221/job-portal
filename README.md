<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

</head>
<body>
  <header>
    <h1>💼 Job Portal — Django 5 Project</h1>
    <p>A full-stack job portal with Celery, Redis, AJAX, and Gemini AI integration.</p>
    <div>
      <span class="tag">Django 5</span>
      <span class="tag">Celery</span>
      <span class="tag">Redis</span>
      <span class="tag">SQLite</span>
      <span class="tag">Gemini AI</span>
      <span class="tag">AJAX</span>
    </div>
  </header>

  <div class="card">
    <h2>🚀 Overview</h2>
    <p>
      The <strong>Job Portal</strong> is a full-stack web application where <strong>job seekers</strong> can upload their resumes, receive <strong>AI-based feedback & insights</strong>, and <strong>apply for jobs</strong> posted by <strong>recruiters</strong>.
      Recruiters can post, manage, and track job applications in real-time. The application uses <strong>Celery + Redis</strong> to handle background AI tasks and <strong>AJAX</strong> to make the dashboards interactive without full page reloads.
    </p>
  </div>

  <div class="card">
    <h2>⚙️ Tech Stack</h2>
    <ul>
      <li><strong>Backend:</strong> Django 5 (Python)</li>
      <li><strong>Database:</strong> SQLite (Django default DB)</li>
      <li><strong>Task Queue:</strong> Celery with Redis broker</li>
      <li><strong>Frontend:</strong> HTML, CSS, JavaScript (with AJAX for dynamic UI)</li>
      <li><strong>AI Integration:</strong> Google Gemini API (for resume insights)</li>
      <li><strong>Async Processing:</strong> Celery background workers for AI and heavy operations</li>
    </ul>
  </div>

  <div class="card">
    <h2>✨ Features</h2>
    <ul>
      <li><strong>👤 User Roles</strong> — Separate logins for <strong>Job Seekers</strong> and <strong>Recruiters</strong>.</li>
      <li><strong>📄 Resume Upload</strong> — Job seekers can upload their resumes (PDF or DOCX).</li>
      <li><strong>🤖 AI Resume Insights</strong> — Gemini API analyzes resumes and provides feedback on strengths, weaknesses, and suggestions.</li>
      <li><strong>📊 Dashboard (AJAX)</strong> — Dynamic, no-page-reload dashboard for both seekers and recruiters.</li>
      <li><strong>📬 Job Posting System</strong> — Recruiters can create, edit, and delete job listings.</li>
      <li><strong>💼 Application Management</strong> — Track applicants for each job with status updates.</li>
      <li><strong>⚙️ Celery Background Tasks</strong> — AI insight generation handled asynchronously without blocking UI.</li>
      <li><strong>🔍 Job Search</strong> — Filter and search jobs by title, company, or skills.</li>
      <li><strong>🧠 AI Insights Dashboard</strong> — Displays formatted feedback, resume score, and skill suggestions.</li>
      <li><strong>🪄 Smart Formatting</strong> — AI insights auto-formatted to clean HTML using a markdown-to-HTML script.</li>
      <li><strong>🧱 Modular Design</strong> — Django apps: <code>account</code>, <code>jobs</code>, and <code>dashboard</code>.</li>
      <li><strong>🕓 Real-time Status</strong> — AJAX updates progress of background tasks (loading indicators).</li>
    </ul>
  </div>

  <div class="card">
    <h2>🧩 Project Setup</h2>
    <p class="note"><strong>Where to run commands:</strong> Each block below shows the exact location to execute the command — e.g., in terminal inside project root or elsewhere.</p>

    <h3>1️⃣ Create Virtual Environment</h3>
    <pre><strong>[terminal: anywhere]</strong>
python -m venv venv
</pre>

    <h3>2️⃣ Activate Virtual Environment</h3>
    <pre><strong>[terminal: project-root]</strong>
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
</pre>

    <h3>3️⃣ Install Dependencies</h3>
    <pre><strong>[terminal: project-root]</strong>
pip install -r requirements.txt
</pre>

    <h3>4️⃣ Run Migrations</h3>
    <pre><strong>[terminal: project-root]</strong>
python manage.py migrate
</pre>

    <h3>5️⃣ Create Superuser</h3>
    <pre><strong>[terminal: project-root]</strong>
python manage.py createsuperuser
</pre>

    <h3>6️⃣ Run Development Server</h3>
    <pre><strong>[terminal: project-root]</strong>
python manage.py runserver
</pre>

    <h3>7️⃣ Start Redis Server</h3>
    <pre><strong>[terminal: system]</strong>
# Linux
sudo service redis-server start

# OR via Docker
docker run -d --name redis -p 6379:6379 redis
</pre>

    <h3>8️⃣ Start Celery Worker</h3>
    <pre><strong>[terminal: project-root]</strong>
celery -A jobportal worker --loglevel=info
</pre>
  </div>

  <div class="card">
    <h2>🔑 Gemini API Integration</h2>
    <p>
      The project integrates <strong>Google Gemini API</strong> for AI-based resume insights.  
      You must set up your <code>GEMINI_API_KEY</code> inside your <code>.env</code> file.
    </p>
    <pre>
# .env file example
SECRET_KEY=your_secret_key
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key
REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
    </pre>
    <p>The AI integration is used in the dashboard to generate resume feedback, skill extraction, and personalized job suggestions.</p>
  </div>

  <div class="card">
    <h2>🧠 AI Features (Gemini Integration)</h2>
    <ul>
      <li><strong>Resume Parsing:</strong> Extracts skills, experience, and achievements from uploaded resumes.</li>
      <li><strong>AI Scoring:</strong> Generates a <em>resume strength score</em> out of 100.</li>
      <li><strong>AI Insights:</strong> Provides improvement suggestions (e.g., “Add measurable results to your achievements”).</li>
      <li><strong>Markdown to HTML Conversion:</strong> AI response text is auto-converted using <code>marked.js</code> to clean HTML.</li>
    </ul>
  </div>

  <div class="card">
    <h2>🧱 Folder Structure</h2>
    <pre>
jobportal/
├── account/             # User accounts, seeker & recruiter profiles
├── jobs/                # Job models, views, search, posting
├── dashboard/           # AI insights, analytics
├── templates/
├── static/
├── media/
├── requirements.txt
├── manage.py
└── README.html
    </pre>
  </div>

  <div class="card">
    <h2>⚙️ Troubleshooting</h2>
    <ul>
      <li><strong>Celery not running:</strong> Make sure Redis is running and Celery worker started.</li>
      <li><strong>AI insights not updating:</strong> Ensure valid <code>GEMINI_API_KEY</code> and Celery worker logs show tasks executing.</li>
      <li><strong>“Cannot filter a query once a slice has been taken”:</strong> Apply filters before slicing a QuerySet.</li>
      <li><strong>Resume insights not formatted:</strong> Ensure <code>marked.js</code> script runs in your template for AI insights formatting.</li>
    </ul>
  </div>

  <div class="card">
    <h2>📜 License & Author</h2>
    <p>
      Developed by <strong>Puneet Yadav</strong>.<br>
      Built with ❤️ using Django 5, Celery, Redis, AJAX, and Gemini API.<br>
      Database: SQLite (default Django DB).
    </p>
  </div>

  <footer>
    <p style="color:#94a3b8; font-size:13px;">
      Last updated: November 2025 — README HTML for Job Portal Project.
    </p>
  </footer>
</body>
</html>
