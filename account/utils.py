import google.generativeai as genai
import json
import threading
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
import re





def send_custom_email(subject, template_name, context, to_email):
    from_email = settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject, 
        body=text_content, 
        from_email=from_email,
         to= [to_email],
         )
    email.attach_alternative(html_content, 'text/html')
     # ✅ Run email sending in a separate thread
    threading.Thread(target=email.send).start()







load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=GEMINI_API_KEY)


#  Gemini job recommender (always returns valid JSON)
def recommend_jobs_with_gemini(resume_text, jobs):
    prompt = f"""
    You are an AI job recommender system.

    Based on the following RESUME text:
    {resume_text}

    And this JOB dataset (list of jobs):
    {list(jobs.values('id', 'title', 'skills', 'location'))}

    Return ONLY a JSON array, with no extra words or formatting.
    The JSON array should look exactly like this:
    [
      {{
        "id": 12,
        "match_score": 87
      }},
      {{
        "id": 15,
        "match_score": 76
      }}
    ]
    No markdown formatting, no explanations, no comments — strictly raw JSON.
    """

    model = genai.GenerativeModel("models/gemini-flash-latest")
    response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
            temperature=0.0
    )
)
                                    
    ai_text = response.text.strip()

    # Clean and extract JSON from response (remove ```json ... ``` wrappers etc.)
    match = re.search(r"\[.*\]", ai_text, re.DOTALL)
    if match:
        ai_text = match.group(0)
    else:
        print("⚠️ Gemini returned unexpected text:", ai_text[:300])

    try:
        return json.loads(ai_text)
    except json.JSONDecodeError:
        print("⚠️ Gemini returned non-JSON response:\n", ai_text[:300])
        return [{"id": j.id, "match_score": 50} for j in jobs[:3]]  # fallback





def extract_text_from_resume(resume_file):
    """
    resume_file: this is a FieldFile object (like seeker_profile.resume)
    """
    if not resume_file:
        return "" 

    try:
        # ✅ Get absolute path of uploaded file
        file_path = resume_file.path  
        

        # Example for PDF resumes
        if file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text.strip()
        else:
            return "Unsupported resume format"
    except Exception as e:
        print("⚠️ Resume extraction error:", e)
        return ""



# def generate_resume_score(seeker_profile, jobs):
#     """
#     Generate an AI-powered resume score using existing Gemini recommendation system.
#     """
#     try:
#         # 1️⃣ Extract resume text
#         resume_text = extract_text_from_resume(seeker_profile.resume)
#         if not resume_text:
#             return {
#                 "score": 0,
#                 "feedback": "Resume text could not be extracted.",
#                 "matched_jobs": []
#             }

#         # 2️⃣ Get job recommendations with scores
#         recommendations = recommend_jobs_with_gemini(resume_text, jobs)
#         if not recommendations:
#             return {
#                 "score": 0,
#                 "feedback": "AI could not analyze your resume at the moment.",
#                 "matched_jobs": []
#             }

#         # 3️⃣ Calculate overall resume score
#         scores = [r.get("match_score", 0) for r in recommendations]
#         avg_score = sum(scores) / len(scores) if scores else 0

#         # 4️⃣ Get top 3 matches for insight
#         top_matches = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:3]
#         matched_jobs = list(
#             jobs.filter(id__in=[m["id"] for m in top_matches])
#             .values("id", "title", "skills", "location")
#         )

#         top_jobs_info = list(
#             jobs.filter(id__in=[m["id"] for m in top_matches])
#             .values("title", "skills", "location")
#         )

#         # 5️⃣ Ask Gemini for structured feedback
#         feedback_prompt = f"""
#         You are an AI career coach.

#         A candidate's resume was analyzed against multiple jobs.
#         The average match score was {avg_score:.2f}.
#         Here are the top job matches:
#         {json.dumps(top_jobs_info, indent=2)}

#         Please provide a short, structured feedback in 3 points:
#         1. Strengths (based on skill alignment)
#         2. Missing or weak areas
#         3. Specific recommendations to improve resume-job match
#         """

#         try:
#             model = genai.GenerativeModel("models/gemini-flash-latest")
#             feedback_response = model.generate_content(feedback_prompt)
#             feedback = feedback_response.text.strip()
#         except Exception as gemini_error:
#             feedback = f"Feedback temporarily unavailable. ({gemini_error})"

#         # 6️⃣ Return final dictionary
#         return {
#             "score": round(avg_score, 2),
#             "feedback": feedback,
#             "matched_jobs": matched_jobs,
#         }

#     except Exception as e:
#         print("⚠️ generate_resume_score error:", e)
#         return {"error": str(e)}

def generate_resume_score(seeker_profile, jobs=None):
    """
    Generate resume score and feedback directly from resume content.
    No dependency on job posts or matched jobs.
    """
    try:
        resume_text = extract_text_from_resume(seeker_profile.resume)
        if not resume_text:
            return {
                "score": 0,
                "feedback": "Resume text could not be extracted. Please upload a clear, text-based PDF or DOCX file.",
                "matched_jobs": []
            }

        # Basic heuristic: measure how complete the resume looks
        word_count = len(resume_text.split())
        score = min(100, max(20, int((word_count / 600) * 100)))  # scale around 600 words

        # Bonus if resume contains important keywords
        keywords = ["python", "django", "api", "project", "experience", "sql", "developer", "engineer"]
        keyword_hits = sum(1 for k in keywords if k.lower() in resume_text.lower())
        score += min(15, keyword_hits * 2)
        score = min(100, score)

        # Ask AI for natural language feedback
        prompt = f"""
        You are a resume reviewer.

        Here is the candidate's resume content:
        {resume_text[:3000]}

        Based on the content above, provide short professional feedback:
        1. Strengths
        2. Weak areas
        3. Suggestions for improvement

        Do not include any numeric score in your response.
        """

        model = genai.GenerativeModel("models/gemini-flash-latest")
        feedback_response = model.generate_content(prompt)
        feedback = feedback_response.text.strip()

        return {
            "score": round(score, 2),
            "feedback": feedback,
            "matched_jobs": []
        }

    except Exception as e:
        print("⚠️ generate_resume_score error:", e)
        return {"score": 0, "feedback": f"Error analyzing resume: {e}", "matched_jobs": []}





# def generate_ai_insight(seeker_profile, matched_jobs):
#     """
#     Return a short, cleaned HTML string for the AI insight.
#     If something fails, return a friendly fallback string.
#     """
#     try:
#         # Extract small resume snippet (limit characters for speed)
#         resume_text = ""
#         if seeker_profile and getattr(seeker_profile, "resume", None):
#             resume_text = extract_text_from_resume(seeker_profile.resume) or ""
#         resume_snippet = resume_text[:250].strip()

#         # Prepare matched jobs short text
#         jobs_text = []
#         for j in matched_jobs[:3]:
#             title = getattr(j, "title", "") or ""
#             loc = getattr(j, "location", "") or ""
#             skills = getattr(j, "skills", "") or ""
#             jobs_text.append(f"{title} — {loc} ({skills})")
#         jobs_text = "\n".join(jobs_text)

#         prompt = f"""
# You are a concise and professional career assistant. Produce a compact, 4-part insight under 180 words:

# Profile Summary: 1 short line.
# Key Strengths: 3 short bullets.
# Improvement Tips: 2 short bullets.
# Growth Direction: 1 short line.


# Resume snippet:
# {resume_snippet}

# Top matched jobs:
# {jobs_text}
# """

#         model = genai.GenerativeModel("models/gemini-flash-latest")
#         resp = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.0))
#         raw = resp.text.strip()

#        # 🧹 Clean up text formatting
#         raw = re.sub(r'\*\*', '', raw)                # remove markdown bolds
#         raw = re.sub(r'-\s+', '• ', raw)              # replace dash bullets with •
#         raw = re.sub(r'\n{2,}', '\n', raw)            # collapse multiple blank lines
#         raw = raw.strip()

#         # ✂️ Limit to 1500 characters max
#         if len(raw) > 1500:
#             raw = raw[:1500].rsplit(' ', 1)[0] + "..."

#         # 🎨 Highlight key headings (HTML)
#         # 🎨 Highlight and style headings cleanly
#         replacements = {
#     r'(?i)\bProfile Summary\b': "<span class='fw-bold text-primary fs-6 d-block mb-1'>Profile Summary</span>",
#     r'(?i)\bKey Strengths\b': "<span class='fw-bold text-success fs-6 d-block mt-3 mb-1'>Key Strengths</span>",
#     r'(?i)\bImprovement Tips\b': "<span class='fw-bold text-warning fs-6 d-block mt-3 mb-1'>Improvement Tips</span>",
#     r'(?i)\bGrowth Direction\b': "<span class='fw-bold text-info fs-6 d-block mt-3 mb-1'>Growth Direction</span>",
# }

#         for pattern, replacement in replacements.items():
#             raw = re.sub(pattern, replacement, raw)


#         # 🧱 Convert newlines to <br> for display
#         html = "<div class='ai-insight-body small text-muted' style='white-space: pre-line;'>" + raw.replace("\n", "<br>") + "</div>"

#         return html
#     except Exception as e:
#         print("⚠️ generate_ai_insight error:", e)
#         return ("<div class='ai-insight-body text-muted small'>"
#                 "AI insight is temporarily unavailable. Try re-evaluating your resume or check back later.</div>")






def generate_ai_insight(seeker_profile, matched_jobs=None):
    """
    Generate AI insight purely from resume content (no job dependency).
    """
    try:
        resume_text = extract_text_from_resume(seeker_profile.resume)
        if not resume_text:
            return "<p class='text-muted small'>AI could not extract text from your resume. Please re-upload.</p>"

        prompt = f"""
        You are an AI career mentor. Read the following resume text and generate a short insight (under 180 words).

        Divide your answer into 4 clear sections:
        1. Profile Summary
        2. Key Strengths
        3. Improvement Tips
        4. Growth Direction

        Resume content:
        {resume_text[:3000]}

        Be concise, professional, and motivational. Avoid mentioning job titles or scores.
        """

        model = genai.GenerativeModel("models/gemini-flash-latest")
        resp = model.generate_content(prompt)
        raw = resp.text.strip()

        # Formatting for display
        raw = re.sub(r'\*\*', '', raw)
        raw = re.sub(r'-\s+', '• ', raw)
        raw = re.sub(r'\n{2,}', '\n', raw)
        raw = raw.strip()

        replacements = {
            r'(?i)\bProfile Summary\b': "<span class='fw-bold text-primary fs-6 d-block mb-1'>Profile Summary</span>",
            r'(?i)\bKey Strengths\b': "<span class='fw-bold text-success fs-6 d-block mt-3 mb-1'>Key Strengths</span>",
            r'(?i)\bImprovement Tips\b': "<span class='fw-bold text-warning fs-6 d-block mt-3 mb-1'>Improvement Tips</span>",
            r'(?i)\bGrowth Direction\b': "<span class='fw-bold text-info fs-6 d-block mt-3 mb-1'>Growth Direction</span>",
        }

        for pattern, replacement in replacements.items():
            raw = re.sub(pattern, replacement, raw)

        html = "<div class='ai-insight-body small text-muted' style='white-space: pre-line;'>" + raw.replace("\n", "<br>") + "</div>"
        return html

    except Exception as e:
        print("⚠️ generate_ai_insight error:", e)
        return ("<div class='ai-insight-body text-muted small'>AI insight temporarily unavailable. Try re-uploading your resume later.</div>")


