from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'uniwese-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 168  # 7 days

# Create the main app
app = FastAPI(title="UniWese API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "student"  # student, admin, college

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None
    created_at: datetime

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None

# Profile Models
class AcademicHistory(BaseModel):
    institution: str
    degree: str
    field: str
    start_year: int
    end_year: Optional[int] = None
    score: Optional[str] = None
    score_type: str = "CGPA"  # CGPA, Percentage

class TestScore(BaseModel):
    test_name: str
    score: str
    date: Optional[str] = None
    details: Optional[dict] = None

class ProfileUpdate(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    target_degree: Optional[str] = None
    target_intake: Optional[str] = None
    academic_history: Optional[List[AcademicHistory]] = None
    test_scores: Optional[List[TestScore]] = None
    bio: Optional[str] = None

class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    profile_id: str
    user_id: str
    phone: Optional[str] = None
    location: Optional[str] = None
    target_degree: Optional[str] = None
    target_intake: Optional[str] = None
    academic_history: List[AcademicHistory] = []
    test_scores: List[TestScore] = []
    documents: List[dict] = []
    bio: Optional[str] = None
    profile_completion: int = 0
    created_at: datetime
    updated_at: datetime

# College Models
class College(BaseModel):
    model_config = ConfigDict(extra="ignore")
    college_id: str
    name: str
    country: str
    city: str
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    description: str
    courses: List[str] = []
    ranking: Optional[int] = None
    tuition_min: Optional[int] = None
    tuition_max: Optional[int] = None
    acceptance_rate: Optional[float] = None
    intakes: List[str] = []
    requirements: dict = {}
    verified: bool = False
    average_rating: float = 0
    total_reviews: int = 0
    created_at: datetime

class CollegeCreate(BaseModel):
    name: str
    country: str
    city: str
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    description: str
    courses: List[str] = []
    ranking: Optional[int] = None
    tuition_min: Optional[int] = None
    tuition_max: Optional[int] = None
    acceptance_rate: Optional[float] = None
    intakes: List[str] = []
    requirements: dict = {}

# Application Models
class ApplicationCreate(BaseModel):
    college_id: str
    course: str
    intake: str
    statement_of_purpose: Optional[str] = None

class Application(BaseModel):
    model_config = ConfigDict(extra="ignore")
    application_id: str
    user_id: str
    college_id: str
    college_name: str
    course: str
    intake: str
    status: str = "submitted"  # submitted, under_review, accepted, rejected, withdrawn
    statement_of_purpose: Optional[str] = None
    documents: List[dict] = []
    submitted_at: datetime
    updated_at: datetime

# Review Models
class ReviewCreate(BaseModel):
    college_id: str
    rating: int = Field(ge=1, le=5)
    title: str
    content: str
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None

class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str
    user_id: str
    user_name: str
    college_id: str
    rating: int
    title: str
    content: str
    pros: List[str] = []
    cons: List[str] = []
    helpful_count: int = 0
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime

# Forum Models
class ThreadCreate(BaseModel):
    title: str
    content: str
    category: str  # admissions, visa, scholarships, general

class Thread(BaseModel):
    model_config = ConfigDict(extra="ignore")
    thread_id: str
    user_id: str
    user_name: str
    title: str
    content: str
    category: str
    replies_count: int = 0
    views: int = 0
    is_pinned: bool = False
    status: str = "active"  # active, closed, hidden
    created_at: datetime

class ReplyCreate(BaseModel):
    thread_id: str
    content: str

class Reply(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reply_id: str
    thread_id: str
    user_id: str
    user_name: str
    content: str
    likes: int = 0
    created_at: datetime

# Loan Models
class LoanInquiryCreate(BaseModel):
    loan_amount: int
    course: str
    college_name: str
    country: str
    contact_phone: str

class LoanInquiry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    inquiry_id: str
    user_id: str
    loan_amount: int
    course: str
    college_name: str
    country: str
    contact_phone: str
    status: str = "pending"  # pending, contacted, approved, rejected
    created_at: datetime

# Document Models
class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str
    user_id: str
    name: str
    file_type: str
    file_size: int
    storage_path: str
    category: str  # transcript, lor, sop, resume, passport, other
    status: str = "uploaded"  # uploaded, verified, rejected
    uploaded_at: datetime

# ============== HELPER FUNCTIONS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str, role: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(request: Request) -> dict:
    # Check cookie first, then Authorization header
    token = request.cookies.get("session_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if it's a session token (from Google OAuth)
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if session:
        expires_at = session.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")
        
        user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    
    # Otherwise, it's a JWT token
    payload = decode_jwt_token(token)
    user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def calculate_profile_completion(profile: dict) -> int:
    total_fields = 7
    completed = 0
    
    if profile.get("phone"): completed += 1
    if profile.get("location"): completed += 1
    if profile.get("target_degree"): completed += 1
    if profile.get("target_intake"): completed += 1
    if profile.get("academic_history") and len(profile["academic_history"]) > 0: completed += 1
    if profile.get("test_scores") and len(profile["test_scores"]) > 0: completed += 1
    if profile.get("documents") and len(profile["documents"]) > 0: completed += 1
    
    return int((completed / total_fields) * 100)

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register")
async def register(data: UserCreate, response: Response):
    # Check if user exists
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = hash_password(data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": data.email,
        "name": data.name,
        "password": hashed_password,
        "role": data.role,
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create empty profile
    profile_doc = {
        "profile_id": f"profile_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "phone": None,
        "location": None,
        "target_degree": None,
        "target_intake": None,
        "academic_history": [],
        "test_scores": [],
        "documents": [],
        "bio": None,
        "profile_completion": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.profiles.insert_one(profile_doc)
    
    token = create_jwt_token(user_id, data.email, data.role)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600
    )
    
    return {
        "user_id": user_id,
        "email": data.email,
        "name": data.name,
        "role": data.role,
        "token": token
    }

@api_router.post("/auth/login")
async def login(data: UserLogin, response: Response):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["user_id"], user["email"], user["role"])
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600
    )
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "picture": user.get("picture"),
        "token": token
    }

@api_router.post("/auth/session")
async def create_session_from_google(request: Request, response: Response):
    """Exchange Emergent OAuth session_id for user session"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Call Emergent Auth to get user data
    async with httpx.AsyncClient() as client_http:
        try:
            auth_response = await client_http.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            auth_data = auth_response.json()
        except Exception as e:
            logger.error(f"Error fetching session data: {e}")
            raise HTTPException(status_code=500, detail="Auth service error")
    
    email = auth_data.get("email")
    name = auth_data.get("name")
    picture = auth_data.get("picture")
    session_token = auth_data.get("session_token")
    
    # Check if user exists
    user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if user:
        # Update existing user
        await db.users.update_one(
            {"email": email},
            {"$set": {"name": name, "picture": picture}}
        )
        user_id = user["user_id"]
        role = user["role"]
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        role = "student"
        user_doc = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "password": None,  # Google auth users don't have password
            "role": role,
            "picture": picture,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
        
        # Create empty profile
        profile_doc = {
            "profile_id": f"profile_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "phone": None,
            "location": None,
            "target_degree": None,
            "target_intake": None,
            "academic_history": [],
            "test_scores": [],
            "documents": [],
            "bio": None,
            "profile_completion": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.profiles.insert_one(profile_doc)
    
    # Store session
    session_doc = {
        "session_id": f"sess_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 3600
    )
    
    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "role": role,
        "picture": picture
    }

@api_router.get("/auth/me")
async def get_current_user_info(request: Request):
    user = await get_current_user(request)
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "picture": user.get("picture")
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# ============== PROFILE ROUTES ==============

@api_router.get("/profile")
async def get_profile(request: Request):
    user = await get_current_user(request)
    profile = await db.profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Include user info
    profile["name"] = user["name"]
    profile["email"] = user["email"]
    profile["picture"] = user.get("picture")
    
    return profile

@api_router.put("/profile")
async def update_profile(data: ProfileUpdate, request: Request):
    user = await get_current_user(request)
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Convert academic history and test scores to dict
    if "academic_history" in update_data:
        update_data["academic_history"] = [h.model_dump() if hasattr(h, 'model_dump') else h for h in update_data["academic_history"]]
    if "test_scores" in update_data:
        update_data["test_scores"] = [s.model_dump() if hasattr(s, 'model_dump') else s for s in update_data["test_scores"]]
    
    # Calculate profile completion
    profile = await db.profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    merged = {**profile, **update_data}
    update_data["profile_completion"] = calculate_profile_completion(merged)
    
    await db.profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": update_data}
    )
    
    updated_profile = await db.profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    updated_profile["name"] = user["name"]
    updated_profile["email"] = user["email"]
    updated_profile["picture"] = user.get("picture")
    
    return updated_profile

@api_router.post("/profile/documents")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(...),
    name: str = Form(...)
):
    user = await get_current_user(request)
    
    # Create storage directory if not exists
    storage_dir = Path("/app/storage/documents") / user["user_id"]
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    storage_filename = f"{document_id}{file_ext}"
    storage_path = storage_dir / storage_filename
    
    # Save file
    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)
    
    doc = {
        "document_id": document_id,
        "name": name,
        "original_filename": file.filename,
        "file_type": file_ext,
        "file_size": len(content),
        "storage_path": str(storage_path),
        "category": category,
        "status": "uploaded",
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add to profile documents
    await db.profiles.update_one(
        {"user_id": user["user_id"]},
        {"$push": {"documents": doc}}
    )
    
    # Recalculate profile completion
    profile = await db.profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    completion = calculate_profile_completion(profile)
    await db.profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"profile_completion": completion, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"document_id": document_id, "message": "Document uploaded successfully"}

@api_router.delete("/profile/documents/{document_id}")
async def delete_document(document_id: str, request: Request):
    user = await get_current_user(request)
    
    await db.profiles.update_one(
        {"user_id": user["user_id"]},
        {"$pull": {"documents": {"document_id": document_id}}}
    )
    
    return {"message": "Document deleted successfully"}

# ============== COLLEGE ROUTES ==============

@api_router.get("/colleges")
async def get_colleges(
    country: Optional[str] = None,
    course: Optional[str] = None,
    min_budget: Optional[int] = None,
    max_budget: Optional[int] = None,
    intake: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    query = {}
    
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    if course:
        query["courses"] = {"$regex": course, "$options": "i"}
    if intake:
        query["intakes"] = {"$regex": intake, "$options": "i"}
    if min_budget:
        query["tuition_min"] = {"$gte": min_budget}
    if max_budget:
        query["tuition_max"] = {"$lte": max_budget}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    colleges = await db.colleges.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.colleges.count_documents(query)
    
    return {
        "colleges": colleges,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/colleges/{college_id}")
async def get_college(college_id: str):
    college = await db.colleges.find_one({"college_id": college_id}, {"_id": 0})
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Get reviews
    reviews = await db.reviews.find(
        {"college_id": college_id, "status": "approved"},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    college["reviews"] = reviews
    return college

@api_router.post("/colleges", dependencies=[])
async def create_college(data: CollegeCreate, request: Request):
    await require_admin(request)
    
    college_id = f"college_{uuid.uuid4().hex[:12]}"
    college_doc = {
        "college_id": college_id,
        **data.model_dump(),
        "verified": False,
        "average_rating": 0,
        "total_reviews": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.colleges.insert_one(college_doc)
    del college_doc["_id"] if "_id" in college_doc else None
    return college_doc

@api_router.put("/colleges/{college_id}")
async def update_college(college_id: str, data: CollegeCreate, request: Request):
    await require_admin(request)
    
    update_data = data.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.colleges.update_one(
        {"college_id": college_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="College not found")
    
    college = await db.colleges.find_one({"college_id": college_id}, {"_id": 0})
    return college

@api_router.delete("/colleges/{college_id}")
async def delete_college(college_id: str, request: Request):
    await require_admin(request)
    
    result = await db.colleges.delete_one({"college_id": college_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="College not found")
    
    return {"message": "College deleted successfully"}

# ============== APPLICATION ROUTES ==============

@api_router.post("/applications")
async def create_application(data: ApplicationCreate, request: Request):
    user = await get_current_user(request)
    
    # Check if college exists
    college = await db.colleges.find_one({"college_id": data.college_id}, {"_id": 0})
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check for duplicate application
    existing = await db.applications.find_one({
        "user_id": user["user_id"],
        "college_id": data.college_id,
        "intake": data.intake
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this college for this intake")
    
    application_id = f"app_{uuid.uuid4().hex[:12]}"
    
    # Get user's documents
    profile = await db.profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    documents = profile.get("documents", []) if profile else []
    
    application_doc = {
        "application_id": application_id,
        "user_id": user["user_id"],
        "user_name": user["name"],
        "user_email": user["email"],
        "college_id": data.college_id,
        "college_name": college["name"],
        "course": data.course,
        "intake": data.intake,
        "status": "submitted",
        "statement_of_purpose": data.statement_of_purpose,
        "documents": documents,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.applications.insert_one(application_doc)
    del application_doc["_id"] if "_id" in application_doc else None
    return application_doc

@api_router.get("/applications")
async def get_my_applications(request: Request):
    user = await get_current_user(request)
    
    applications = await db.applications.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("submitted_at", -1).to_list(100)
    
    return applications

@api_router.get("/applications/{application_id}")
async def get_application(application_id: str, request: Request):
    user = await get_current_user(request)
    
    application = await db.applications.find_one(
        {"application_id": application_id},
        {"_id": 0}
    )
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Only owner or admin can view
    if application["user_id"] != user["user_id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return application

@api_router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    request: Request
):
    await require_admin(request)
    body = await request.json()
    status = body.get("status")
    
    if status not in ["submitted", "under_review", "accepted", "rejected", "withdrawn"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.applications.update_one(
        {"application_id": application_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = await db.applications.find_one({"application_id": application_id}, {"_id": 0})
    return application

@api_router.delete("/applications/{application_id}")
async def withdraw_application(application_id: str, request: Request):
    user = await get_current_user(request)
    
    application = await db.applications.find_one({"application_id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.applications.update_one(
        {"application_id": application_id},
        {"$set": {"status": "withdrawn", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Application withdrawn"}

# ============== REVIEW ROUTES ==============

@api_router.post("/reviews")
async def create_review(data: ReviewCreate, request: Request):
    user = await get_current_user(request)
    
    # Check if college exists
    college = await db.colleges.find_one({"college_id": data.college_id})
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check for existing review
    existing = await db.reviews.find_one({
        "user_id": user["user_id"],
        "college_id": data.college_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already reviewed this college")
    
    review_id = f"review_{uuid.uuid4().hex[:12]}"
    review_doc = {
        "review_id": review_id,
        "user_id": user["user_id"],
        "user_name": user["name"],
        "college_id": data.college_id,
        "rating": data.rating,
        "title": data.title,
        "content": data.content,
        "pros": data.pros or [],
        "cons": data.cons or [],
        "helpful_count": 0,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.reviews.insert_one(review_doc)
    return {"review_id": review_id, "message": "Review submitted for moderation"}

@api_router.get("/reviews/college/{college_id}")
async def get_college_reviews(college_id: str, page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    reviews = await db.reviews.find(
        {"college_id": college_id, "status": "approved"},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.reviews.count_documents({"college_id": college_id, "status": "approved"})
    
    return {
        "reviews": reviews,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.put("/reviews/{review_id}/moderate")
async def moderate_review(review_id: str, request: Request):
    await require_admin(request)
    body = await request.json()
    status = body.get("status")
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.reviews.update_one(
        {"review_id": review_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Update college rating if approved
    if status == "approved":
        review = await db.reviews.find_one({"review_id": review_id})
        college_id = review["college_id"]
        
        # Calculate new average
        reviews = await db.reviews.find(
            {"college_id": college_id, "status": "approved"}
        ).to_list(1000)
        
        if reviews:
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
            await db.colleges.update_one(
                {"college_id": college_id},
                {"$set": {"average_rating": round(avg_rating, 1), "total_reviews": len(reviews)}}
            )
    
    return {"message": f"Review {status}"}

# ============== FORUM ROUTES ==============

@api_router.get("/forum/threads")
async def get_threads(category: Optional[str] = None, page: int = 1, limit: int = 20):
    query = {"status": "active"}
    if category:
        query["category"] = category
    
    skip = (page - 1) * limit
    threads = await db.forum_threads.find(query, {"_id": 0}).sort([
        ("is_pinned", -1),
        ("created_at", -1)
    ]).skip(skip).limit(limit).to_list(limit)
    
    total = await db.forum_threads.count_documents(query)
    
    return {
        "threads": threads,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.post("/forum/threads")
async def create_thread(data: ThreadCreate, request: Request):
    user = await get_current_user(request)
    
    thread_id = f"thread_{uuid.uuid4().hex[:12]}"
    thread_doc = {
        "thread_id": thread_id,
        "user_id": user["user_id"],
        "user_name": user["name"],
        "title": data.title,
        "content": data.content,
        "category": data.category,
        "replies_count": 0,
        "views": 0,
        "is_pinned": False,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.forum_threads.insert_one(thread_doc)
    del thread_doc["_id"] if "_id" in thread_doc else None
    return thread_doc

@api_router.get("/forum/threads/{thread_id}")
async def get_thread(thread_id: str):
    thread = await db.forum_threads.find_one({"thread_id": thread_id}, {"_id": 0})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment views
    await db.forum_threads.update_one(
        {"thread_id": thread_id},
        {"$inc": {"views": 1}}
    )
    
    # Get replies
    replies = await db.forum_replies.find(
        {"thread_id": thread_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    
    thread["replies"] = replies
    return thread

@api_router.post("/forum/replies")
async def create_reply(data: ReplyCreate, request: Request):
    user = await get_current_user(request)
    
    # Check thread exists
    thread = await db.forum_threads.find_one({"thread_id": data.thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    reply_id = f"reply_{uuid.uuid4().hex[:12]}"
    reply_doc = {
        "reply_id": reply_id,
        "thread_id": data.thread_id,
        "user_id": user["user_id"],
        "user_name": user["name"],
        "content": data.content,
        "likes": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.forum_replies.insert_one(reply_doc)
    
    # Update reply count
    await db.forum_threads.update_one(
        {"thread_id": data.thread_id},
        {"$inc": {"replies_count": 1}}
    )
    
    del reply_doc["_id"] if "_id" in reply_doc else None
    return reply_doc

@api_router.put("/forum/threads/{thread_id}/moderate")
async def moderate_thread(thread_id: str, request: Request):
    await require_admin(request)
    body = await request.json()
    status = body.get("status")
    is_pinned = body.get("is_pinned")
    
    update = {}
    if status:
        update["status"] = status
    if is_pinned is not None:
        update["is_pinned"] = is_pinned
    
    if not update:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.forum_threads.update_one(
        {"thread_id": thread_id},
        {"$set": update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return {"message": "Thread updated"}

# ============== LOAN ROUTES ==============

@api_router.post("/loans/inquiry")
async def create_loan_inquiry(data: LoanInquiryCreate, request: Request):
    user = await get_current_user(request)
    
    inquiry_id = f"loan_{uuid.uuid4().hex[:12]}"
    inquiry_doc = {
        "inquiry_id": inquiry_id,
        "user_id": user["user_id"],
        "user_name": user["name"],
        "user_email": user["email"],
        "loan_amount": data.loan_amount,
        "course": data.course,
        "college_name": data.college_name,
        "country": data.country,
        "contact_phone": data.contact_phone,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.loan_inquiries.insert_one(inquiry_doc)
    return {"inquiry_id": inquiry_id, "message": "Loan inquiry submitted successfully"}

@api_router.get("/loans/inquiries")
async def get_my_loan_inquiries(request: Request):
    user = await get_current_user(request)
    
    inquiries = await db.loan_inquiries.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return inquiries

# ============== ADMIN ROUTES ==============

@api_router.get("/admin/users")
async def admin_get_users(request: Request, page: int = 1, limit: int = 20):
    await require_admin(request)
    
    skip = (page - 1) * limit
    users = await db.users.find({}, {"_id": 0, "password": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/admin/applications")
async def admin_get_applications(request: Request, status: Optional[str] = None, page: int = 1, limit: int = 20):
    await require_admin(request)
    
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    applications = await db.applications.find(query, {"_id": 0}).sort("submitted_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.applications.count_documents(query)
    
    return {
        "applications": applications,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/admin/reviews")
async def admin_get_reviews(request: Request, status: Optional[str] = None, page: int = 1, limit: int = 20):
    await require_admin(request)
    
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    reviews = await db.reviews.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.reviews.count_documents(query)
    
    return {
        "reviews": reviews,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/admin/loan-inquiries")
async def admin_get_loan_inquiries(request: Request, status: Optional[str] = None, page: int = 1, limit: int = 20):
    await require_admin(request)
    
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    inquiries = await db.loan_inquiries.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.loan_inquiries.count_documents(query)
    
    return {
        "inquiries": inquiries,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.put("/admin/loan-inquiries/{inquiry_id}/status")
async def admin_update_loan_status(inquiry_id: str, request: Request):
    await require_admin(request)
    body = await request.json()
    status = body.get("status")
    
    if status not in ["pending", "contacted", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.loan_inquiries.update_one(
        {"inquiry_id": inquiry_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    return {"message": f"Status updated to {status}"}

@api_router.get("/admin/stats")
async def admin_get_stats(request: Request):
    await require_admin(request)
    
    total_users = await db.users.count_documents({})
    total_applications = await db.applications.count_documents({})
    total_colleges = await db.colleges.count_documents({})
    pending_reviews = await db.reviews.count_documents({"status": "pending"})
    pending_applications = await db.applications.count_documents({"status": "submitted"})
    
    return {
        "total_users": total_users,
        "total_applications": total_applications,
        "total_colleges": total_colleges,
        "pending_reviews": pending_reviews,
        "pending_applications": pending_applications
    }

# ============== ACCOMMODATION ROUTES ==============

@api_router.get("/accommodations")
async def get_accommodations(country: Optional[str] = None, city: Optional[str] = None):
    # This returns a list of accommodation resources/links
    accommodations = [
        {
            "id": "1",
            "name": "University Housing Board",
            "type": "Official",
            "countries": ["USA", "UK", "Canada"],
            "url": "https://example.com/housing",
            "description": "Official university housing resources"
        },
        {
            "id": "2",
            "name": "Student Room Finder",
            "type": "Platform",
            "countries": ["USA", "UK", "Australia"],
            "url": "https://example.com/rooms",
            "description": "Find shared apartments and rooms"
        },
        {
            "id": "3",
            "name": "International Student Housing",
            "type": "Platform",
            "countries": ["Germany", "France", "Netherlands"],
            "url": "https://example.com/international",
            "description": "Housing specifically for international students"
        }
    ]
    
    if country:
        accommodations = [a for a in accommodations if country in a["countries"]]
    
    return accommodations

# ============== HEALTH CHECK ==============

@api_router.get("/")
async def root():
    return {"message": "UniWese API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
