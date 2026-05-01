from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

load_dotenv()

app = FastAPI(
    title="WorkHub API",
    description="A freelancer booking platform",
    version="0.3.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("DB_NAME")]

# Password encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "workhub-super-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# JWT bearer scheme
security = HTTPBearer()

# -----------------------------------------------
# MODELS
# -----------------------------------------------

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    role: str

class LoginUser(BaseModel):
    email: str
    password: str

class FreelancerProfile(BaseModel):
    bio: str
    skills: list
    hourly_rate: int

# -----------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_token(email: str, role: str):
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    data = {"email": email, "role": role, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# -----------------------------------------------
# JWT GUARD
# -----------------------------------------------

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        role = payload.get("role")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.users.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"email": email, "role": role, "name": user["name"]}

def require_role(role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(
                status_code=403,
                detail=f"Only {role}s can do this"
            )
        return current_user
    return role_checker

# -----------------------------------------------
# ROUTES
# -----------------------------------------------

@app.get("/")
def root():
    return {"message": "Welcome to WorkHub API 🚀"}

# --- AUTH ---
@app.post("/auth/register")
async def register(user: RegisterUser):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.role not in ["client", "freelancer"]:
        raise HTTPException(status_code=400, detail="Role must be client or freelancer")
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role,
        "created_at": datetime.utcnow().isoformat()
    }
    await db.users.insert_one(new_user)
    return {"message": f"Welcome to WorkHub, {user.name}! 🎉", "role": user.role}

@app.post("/auth/login")
async def login(user: LoginUser):
    found = await db.users.find_one({"email": user.email})
    if not found:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(found["email"], found["role"])
    return {
        "message": f"Welcome back, {found['name']}! 🚀",
        "token": token,
        "role": found["role"]
    }

# --- FREELANCER PROFILE ---
@app.get("/freelancers")
async def get_freelancers():
    freelancers = []
    async for f in db.freelancer_profiles.find({}, {"_id": 0}):
        freelancers.append(f)
    return {"freelancers": freelancers}

# 🔐 Protected — only freelancers can create a profile
@app.post("/freelancers/profile")
async def create_profile(
    profile: FreelancerProfile,
    current_user: dict = Depends(require_role("freelancer"))
):
    existing = await db.freelancer_profiles.find_one({"email": current_user["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    new_profile = {
        "name": current_user["name"],
        "email": current_user["email"],
        "bio": profile.bio,
        "skills": profile.skills,
        "hourly_rate": profile.hourly_rate,
        "created_at": datetime.utcnow().isoformat()
    }
    await db.freelancer_profiles.insert_one(new_profile)
    # Remove _id before returning
    new_profile.pop("_id", None)
    return {"message": "WorkHub profile created! 🎉", "data": new_profile}

# 🔐 Protected — get my own info
@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# --- TEST ---
@app.get("/test-db")
async def test_db():
    try:
        await client.admin.command("ping")
        users_count = await db.users.count_documents({})
        profiles_count = await db.freelancer_profiles.count_documents({})
        return {
            "status": "✅ MongoDB connected successfully!",
            "database": os.getenv("DB_NAME"),
            "collections": {
                "users": f"{users_count} documents",
                "freelancer_profiles": f"{profiles_count} documents"
            }
        }
    except Exception as e:
        return {"status": "❌ MongoDB connection failed!", "error": str(e)}

        # -----------------------------------------------
# SERVICES
# -----------------------------------------------

class Service(BaseModel):
    title: str
    description: str
    price: int
    duration_mins: int

# 🔐 Only freelancers can add services
@app.post("/services")
async def add_service(
    service: Service,
    current_user: dict = Depends(require_role("freelancer"))
):
    new_service = {
        "freelancer_name": current_user["name"],
        "freelancer_email": current_user["email"],
        "title": service.title,
        "description": service.description,
        "price": service.price,
        "duration_mins": service.duration_mins,
        "created_at": datetime.utcnow().isoformat()
    }
    await db.services.insert_one(new_service)
    new_service.pop("_id", None)
    return {"message": "Service added to WorkHub! 🎉", "data": new_service}

# Anyone can browse services
@app.get("/services")
async def get_services():
    services = []
    async for s in db.services.find({}, {"_id": 0}):
        services.append(s)
    return {"services": services}

# -----------------------------------------------
# BOOKINGS
# -----------------------------------------------

class Booking(BaseModel):
    freelancer_email: str
    service_title: str
    date: str        # example: "2026-05-01"
    time: str        # example: "10:00 AM"
    message: str     # client message to freelancer

# 🔐 Only clients can make bookings
@app.post("/bookings")
async def create_booking(
    booking: Booking,
    current_user: dict = Depends(require_role("client"))
):
    # Check if service exists
    service = await db.services.find_one({
        "freelancer_email": booking.freelancer_email,
        "title": booking.service_title
    })
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    new_booking = {
        "client_name": current_user["name"],
        "client_email": current_user["email"],
        "freelancer_email": booking.freelancer_email,
        "service_title": booking.service_title,
        "date": booking.date,
        "time": booking.time,
        "message": booking.message,
        "status": "pending",       # pending → confirmed → completed
        "created_at": datetime.utcnow().isoformat()
    }
    await db.bookings.insert_one(new_booking)
    new_booking.pop("_id", None)
    return {"message": "Booking created on WorkHub! 🎉", "data": new_booking}

# 🔐 Get my bookings — works for both client and freelancer
@app.get("/bookings/mine")
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    bookings = []
    if current_user["role"] == "client":
        # Client sees bookings they made
        async for b in db.bookings.find(
            {"client_email": current_user["email"]}, {"_id": 0}
        ):
            bookings.append(b)
    else:
        # Freelancer sees bookings made for them
        async for b in db.bookings.find(
            {"freelancer_email": current_user["email"]}, {"_id": 0}
        ):
            bookings.append(b)
    return {"bookings": bookings}

# 🔐 Freelancer can confirm or cancel a booking
@app.patch("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    status: str,
    current_user: dict = Depends(require_role("freelancer"))
):
    if status not in ["confirmed", "cancelled", "completed"]:
        raise HTTPException(status_code=400, detail="Status must be confirmed, cancelled or completed")

    from bson import ObjectId
    result = await db.bookings.update_one(
        {
            "_id": ObjectId(booking_id),
            "freelancer_email": current_user["email"]
        },
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"message": f"Booking {status} successfully! ✅"}

# -----------------------------------------------
# REVIEWS
# -----------------------------------------------

class Review(BaseModel):
    freelancer_email: str
    rating: int        # 1 to 5 stars
    comment: str

# 🔐 Only clients can leave reviews
@app.post("/reviews")
async def add_review(
    review: Review,
    current_user: dict = Depends(require_role("client"))
):
    # Rating must be between 1 and 5
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Check if client actually booked this freelancer
    booking = await db.bookings.find_one({
        "client_email": current_user["email"],
        "freelancer_email": review.freelancer_email
    })
    if not booking:
        raise HTTPException(status_code=400, detail="You can only review freelancers you have booked")

    # Check if already reviewed
    existing = await db.reviews.find_one({
        "client_email": current_user["email"],
        "freelancer_email": review.freelancer_email
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this freelancer")

    new_review = {
        "client_name": current_user["name"],
        "client_email": current_user["email"],
        "freelancer_email": review.freelancer_email,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": datetime.utcnow().isoformat()
    }
    await db.reviews.insert_one(new_review)
    new_review.pop("_id", None)

    # Update freelancer's average rating
    all_reviews = []
    async for r in db.reviews.find({"freelancer_email": review.freelancer_email}):
        all_reviews.append(r["rating"])
    avg_rating = sum(all_reviews) / len(all_reviews)

    await db.freelancer_profiles.update_one(
        {"email": review.freelancer_email},
        {"$set": {"avg_rating": round(avg_rating, 1)}}
    )

    return {"message": "Review added! ⭐", "data": new_review}

# Anyone can see reviews for a freelancer
@app.get("/reviews/{freelancer_email}")
async def get_reviews(freelancer_email: str):
    reviews = []
    async for r in db.reviews.find(
        {"freelancer_email": freelancer_email}, {"_id": 0}
    ):
        reviews.append(r)
    return {"reviews": reviews}