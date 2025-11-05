

from celery import shared_task
import json, hashlib, logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from job.models import Job
from application.models import Application
from .utils import extract_text_from_resume, recommend_jobs_with_gemini, generate_resume_score, generate_ai_insight


logger = logging.getLogger(__name__)



# @shared_task
# def dashboard_task(user_id):
#     """
#     Background Celery task to calculate resume score,
#     recommendations, and AI insights for a seeker.
#     """
#     User = get_user_model()
    
#     try:
#         print(f"🚀 Celery: Running dashboard_task for user {user_id}")
#         user = User.objects.get(id=user_id)
#         seeker_profile = user.seekerprofile
#         jobs = Job.objects.all()

#         # 🧠 Step 1: Generate resume score + matched jobs
#         result = generate_resume_score(seeker_profile, jobs)
#         seeker_profile.resume_score = result.get("score", 0)
#         seeker_profile.ai_feedback = result.get("feedback", "")
#         seeker_profile.save()

#         # 🧠 Step 2: Generate AI insight HTML
#         matched_job_objects = jobs.filter(
#             id__in=[j["id"] for j in result.get("matched_jobs", [])]
#         )
#         insight_html = generate_ai_insight(seeker_profile, matched_job_objects)

#         seeker_profile.ai_insight = insight_html
#         seeker_profile.save()

#         print("✅ Celery: Dashboard task completed successfully.")
#         return {"status": "success", "user": user.name}

#     except Exception as e:
#         print(f"❌ Celery: Error in dashboard_task → {e}")
#         return {"status": "error", "message": str(e)}


def get_resume_hash(seeker_profile):
    """Create hash to detect resume changes"""
    resume = getattr(seeker_profile, "resume", None)
    if not resume or not hasattr(resume, "name"):
        return "no_resume"
    # use file name + size + modified time-like attribute (safe fallback)
    size = getattr(resume, "size", 0)
    uploaded = getattr(resume, "uploaded_at", "") or getattr(resume, "modified_time", "")
    hash_input = f"{resume.name}_{size}_{uploaded}"
    return hashlib.md5(hash_input.encode()).hexdigest()


@shared_task
def generate_seeker_dashboard_data(user_id):
    """
    Background Celery task: compute resume analysis, recommended jobs and AI insight.
    Stores results in cache keyed by user id + resume hash to avoid showing stale data.
    Returns a JSON-serializable dict.
    """
    print(f"🚀 Celery started for user {user_id}")
    Result = {}
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        seeker_profile = getattr(user, "seekerprofile", None)
        if not seeker_profile:
            return {"error": "Seeker profile not found"}

        resume_hash = get_resume_hash(seeker_profile)
        print(f"✅ Resume hash: {resume_hash}")

        # exclude jobs already applied by this user
        jobs_qs = Job.objects.exclude(
            id__in=Application.objects.filter(seeker=user).values_list("job_id", flat=True)
        )
        print(f"✅ Jobs fetched: {jobs_qs.count()}")

        # --- Resume analysis (score, feedback, matched_jobs) ---
        resume_data = generate_resume_score(seeker_profile, jobs_qs)
        print("✅ Resume analysis returned")

        # normalize matched_jobs to a list of dicts (safe for cache/JSON)
        matched_jobs_raw = []
        if isinstance(resume_data, dict):
            raw = resume_data.get("matched_jobs", [])
            for item in raw:
                if isinstance(item, dict):
                    # already dict
                    matched_jobs_raw.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "skills": item.get("skills", ""),
                        "location": item.get("location", "")
                    })
                else:
                    # model instance or unknown object
                    matched_jobs_raw.append({
                        "id": getattr(item, "id", None),
                        "title": getattr(item, "title", "") or "",
                        "skills": getattr(item, "skills", "") or "",
                        "location": getattr(item, "location", "") or ""
                    })
            # replace in resume_data (safe)
            resume_data["matched_jobs"] = matched_jobs_raw
        else:
            # ensure it's always a dict
            resume_data = {"score": 0, "feedback": "", "matched_jobs": []}

        # cache resume analysis
        cache.set(f"resume_analysis_{user.id}_{resume_hash}", resume_data, timeout=3600)
        Result["resume_data"] = resume_data
        print("✅ Resume data cached")

        # --- Recommended jobs from Gemini ---
        resume_text = extract_text_from_resume(seeker_profile.resume) or ""
        ai_response = recommend_jobs_with_gemini(resume_text, jobs_qs)
        if isinstance(ai_response, str):
            try:
                ai_response = json.loads(ai_response)
            except Exception:
                ai_response = []

        # convert ai_response to {job_id: score}
        job_scores = {}
        for item in ai_response:
            if isinstance(item, dict) and item.get("id") is not None:
                try:
                    job_scores[int(item["id"])] = int(item.get("match_score", 0))
                except Exception:
                    # safe fallback
                    job_scores[int(item.get("id"))] = 0

        # fetch job objects for valid IDs and attach match_score
        recommended_jobs = []
        if job_scores:
            qs = Job.objects.filter(id__in=list(job_scores.keys())).values("id", "title", "skills", "location")
            for j in qs:
                j = dict(j)
                j["match_score"] = job_scores.get(j["id"], 0)
                recommended_jobs.append(j)
            recommended_jobs = sorted(recommended_jobs, key=lambda x: x["match_score"], reverse=True)

        cache.set(f"recommended_jobs_{user.id}_{resume_hash}", recommended_jobs, timeout=3600)
        Result["recommended_jobs"] = recommended_jobs
        print("✅ Recommended jobs cached")

        # --- AI Insight (HTML) ---
        # Note: generate_ai_insight expects matched_jobs list; pass the normalized matched_jobs
        matched_job_objects = Job.objects.filter(
        id__in=[j["id"] for j in resume_data.get("matched_jobs", []) if j.get("id")]
        )
        ai_insight_html = generate_ai_insight(seeker_profile, matched_job_objects)
        cache.set(f"ai_insight_{user.id}_{resume_hash}", ai_insight_html, timeout=3600)
        Result["ai_insight"] = ai_insight_html
        print("✅ AI insight cached")

    except Exception as err:
        import traceback
        traceback.print_exc()
        Result["error"] = str(err)
        # --- Save key metrics to DB for sidebar sync ---
    try:
        score = Result.get("resume_data", {}).get("score", 0)
        feedback = Result.get("resume_data", {}).get("feedback", "")

        # ✅ Update only existing fields
        seeker_profile.resume_score = score or 0
        seeker_profile.ai_feedback = feedback or ""
        seeker_profile.save(update_fields=["resume_score", "ai_feedback"])

        print(f"✅ DB Sync Complete → score={score}, feedback length={len(feedback)}")

    except Exception as e:
        print(f"⚠️ Could not update seeker_profile → {e}")



    print("🏁 Celery finished")
    # ensure result is JSON serializable
    return json.loads(json.dumps(Result, default=str))

