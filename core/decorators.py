
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseForbidden

error_403_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Access Forbidden</title>
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .container {
        background: rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        backdrop-filter: blur(12px) saturate(180%);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        padding: 60px 50px;
        text-align: center;
        max-width: 500px;
    }
    .header-line {
        font-size: 36px;
        font-weight: 700;
        color: #dc3545;
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }
    .separator {
        color: #555;
        font-weight: 600;
    }
    p {
        font-size: 16px;
        color: #333;
        margin-bottom: 30px;
        line-height: 1.5;
    }
    a.button {
        display: inline-block;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        color: #fff;
        padding: 14px 32px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    a.button:hover {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        transform: translateY(-2px);
    }
</style>
</head>
<body>
    <div class="container">
        <div class="header-line">
            <span>403</span>
            <span class="separator">—</span>
            <span>Access Forbidden</span>
        </div>
        <p>Sorry! You don’t have permission to access this page.<br>
           Please contact support or return to the home page.</p>
        <a href="/" class="button">Return to Home</a>
    </div>
</body>
</html>
"""

def role_required(required_role):
    """Decorator to restrict views by user role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if required_role == "seeker" and user.is_recruiter:
                return HttpResponseForbidden(error_403_html)
            if required_role == "recruiter" and not user.is_recruiter:
                return HttpResponseForbidden(error_403_html)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
