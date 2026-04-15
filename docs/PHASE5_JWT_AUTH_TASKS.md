# 🔐 Phase 5: JWT Authentication System - Atomic Task Breakdown

**Project**: Appt - Yoga Studio Booking System  
**Phase**: Phase 5 - User Authentication & Authorization  
**Status**: 📋 Planning Stage  
**Created**: 2026-04-15  
**Owner**: Rogers (AI Assistant)  

---

## 🎯 Phase Goal

实现完整的 JWT 认证系统，包括：
- 用户注册/登录功能
- Token 自动刷新机制
- 路由权限控制
- API 接口鉴权保护
- 前端状态管理集成

---

## 📊 Task Dependency Map

```
Phase 5 Overview:
├── Backend (Tasks 1-8)
│   ├── User Model & Database → Schemas → Auth Endpoints → Security Middleware
│   └── Admin Seed Script → Unit Tests
│
├── Frontend (Tasks 9-16)  
│   ├── Auth Store → Login/Register Pages → Router Guards
│   └── Axios Interceptors → UI Components
│
└── Integration (Tasks 17-20)
    └── E2E Tests → Documentation → Security Audit
```

---

## 🔨 Backend Tasks (8 Atomic Tasks)

### **Task 5.1: Create User Model** ⏱️ ~30 min
**Priority**: P0 - Critical Path  
**Dependencies**: None  
**Files to Create/Modify**:
- CREATE: `backend/app/db/models/user.py`
- MODIFY: `backend/app/db/models/__init__.py`

**Acceptance Criteria**:
```python
# User model should have:
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # user/admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
```

**Testing**: 
- [ ] Model can be imported without errors
- [ ] Table creation SQL generated correctly
- [ ] All fields have proper constraints (unique, not null, etc.)

---

### **Task 5.2: Create User Schemas** ⏱️ ~20 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task 5.1 Complete  
**Files to Create/Modify**:
- CREATE: `backend/app/schemas/user.py`
- MODIFY: `backend/app/schemas/__init__.py`

**Acceptance Criteria**:
```python
# Required schemas:
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)  # Min 8 chars

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    
# Nesting for FastAPI responses
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
```

**Testing**:
- [ ] Pydantic validation rejects invalid emails
- [ ] Password minimum length enforced (8 chars)
- [ ] Username length validated (3-100 chars)

---

### **Task 5.3: Create Auth Endpoints** ⏱️ ~45 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task 5.2 Complete  
**Files to Create/Modify**:
- CREATE: `backend/app/api/v1/auth.py`
- MODIFY: `backend/app/api/v1/__init__.py` (register router)

**Acceptance Criteria**:
```python
# Required endpoints:

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user → Hash password → Create user → Return JWT token"""
    
@router.post("/login", response_model=TokenResponse)  
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Verify credentials → Generate JWT → Return token"""
    
@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info from token"""

# Helper function to add to auth.py:
def get_current_user(db: Session, token: str = Depends(oauth2_scheme)) -> User:
    """Dependency to extract and validate JWT token, return User object"""
```

**API Contract**:
- POST `/api/v1/auth/register` → Returns `{access_token, token_type}` or HTTP 400 (email exists)
- POST `/api/v1/auth/login` → Returns `{access_token, token_type}` or HTTP 401 (wrong password)
- GET `/api/v1/auth/me` → Returns user info or HTTP 401 (invalid token)

**Testing**:
- [ ] Registration creates user in DB with hashed password
- [ ] Duplicate email rejected with clear error message
- [ ] Login returns JWT token for valid credentials  
- [ ] Invalid login returns 401 Unauthorized
- [ ] /me endpoint requires valid JWT in Authorization header

---

### **Task 5.4: Update Security Middleware** ⏱️ ~25 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task 5.3 Complete  
**Files to Create/Modify**:
- MODIFY: `backend/app/core/security.py` (add get_current_user function)
- MODIFY: `backend/app/main.py` (import and use dependency)

**Acceptance Criteria**:
```python
# Add to security.py:

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get current authenticated user.
    
    1. Verify JWT token using verify_token()
    2. Extract email from payload (sub field)
    3. Query DB for user by email
    4. Return user or raise HTTPException(401)
    
    Usage in endpoints:
        async def some_protected_endpoint(current_user: User = Depends(get_current_user)):
            # current_user is guaranteed to be authenticated here
```

**OAuth2 Configuration**:
```python
# Add to security.py imports and setup:
from fastapi import Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT",
    description="Provide JWT bearer token for authentication"
)
```

**Testing**:
- [ ] Endpoints with `Depends(get_current_user)` reject requests without token
- [ ] Invalid/expired tokens return HTTP 401
- [ ] Valid tokens return correct User object in dependency injection

---

### **Task 5.5: Protect Admin Routes** ⏱️ ~20 min  
**Priority**: P1 - Important  
**Dependencies**: Task 5.4 Complete  
**Files to Modify**:
- MODIFY: `backend/app/api/v1/instructors.py` (add role check if admin-only)
- MODIFY: `backend/app/api/v1/schedules.py` (protect CRUD operations)
- MODIFY: `backend/app/api/v1/bookings.py` (protect admin endpoints)

**Acceptance Criteria**:
```python
# Add role-based access control function to security.py:

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency that ensures user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Usage example in instructors.py:
@router.delete("/{instructor_id}")  # Admin-only operation
async def delete_instructor(
    instructor_id: int, 
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)  # ← Role check
):
    # Only admins can reach this code
```

**Testing**:
- [ ] Regular user token cannot access admin endpoints (HTTP 403)
- [ ] Admin user token can access all endpoints successfully
- [ ] Error message clearly states "Admin privileges required"

---

### **Task 5.6: Create Admin User Seeder** ⏱️ ~15 min  
**Priority**: P1 - Important  
**Dependencies**: Task 5.3 Complete (login endpoint must exist)  
**Files to Create/Modify**:
- MODIFY: `backend/scripts/seed_data.py` (add admin user creation)

**Acceptance Criteria**:
```python
# Add to seed_data.py main() function:

def create_admin_user(db: Session):
    """Create initial admin user if not exists."""
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(
        (User.email == "admin@appt.local") | 
        (User.username == "admin")
    ).first()
    
    if existing_admin:
        print("✓ Admin user already exists")
        return existing_admin
    
    # Create new admin with hashed password
    from app.core.security import hash_password
    
    admin = User(
        email="admin@appt.local",
        username="admin",
        hashed_password=hash_password(settings.ADMIN_PASSWORD),  # From .env
        role="admin",
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✓ Created admin user: {admin.username}")
    return admin

# Call in main():
if __name__ == "__main__":
    # ... existing seeding code ...
    create_admin_user(db_session)  # Add this line
```

**Testing**:
- [ ] Running seed script creates admin user with role="admin"
- [ ] Password is hashed using bcrypt (not plain text in DB)
- [ ] Second run doesn't duplicate admin account
- [ ] Can login with admin credentials successfully

---

### **Task 5.7: Update .env.example** ⏱️ ~10 min  
**Priority**: P2 - Documentation  
**Dependencies**: Task 5.6 Complete  
**Files to Create/Modify**:
- MODIFY: `backend/.env.example` (add auth-related variables)

**Acceptance Criteria**:
```bash
# Add these lines to .env.example:

# ==================== Authentication Configuration ====================

# JWT Token Settings (CRITICAL - Change in production!)
SECRET_KEY=change_this_to_a_random_512bit_key_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours default

# Admin Account Credentials (Change after first setup!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_admin_password_in_production

# Security Recommendations:
# - SECRET_KEY should be at least 32 random bytes (base64 encoded)
# - Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
# - ADMIN_PASSWORD should use bcrypt cost factor >= 12 for production

# ==================== End of Auth Configuration ===================
```

**Testing**:
- [ ] All new variables documented with clear descriptions
- [ ] Security warnings included in comments
- [ ] Generation command provided for SECRET_KEY

---

### **Task 5.8: Backend Unit Tests** ⏱️ ~40 min  
**Priority**: P1 - Important  
**Dependencies**: Tasks 5.3, 5.4, 5.6 Complete  
**Files to Create/Modify**:
- CREATE: `backend/tests/test_auth.py`

**Acceptance Criteria**:
```python
# Required test cases (pytest + httpx):

class TestAuthEndpoints:
    
    async def test_register_new_user(self, client):
        """POST /register - Creates user and returns token"""
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser", 
            "password": "securepassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_register_duplicate_email(self, client):
        """POST /register - Rejects duplicate email with HTTP 400"""
        # First registration succeeds
        await client.post("/auth/register", json={...})  
        # Second fails
        response = await client.post("/auth/register", json={...})
        assert response.status_code == 400
    
    async def test_login_success(self, client):
        """POST /login - Returns token for valid credentials"""
        # Register first
        await client.post("/auth/register", json={
            "email": "login_test@example.com",
            "username": "logintest",
            "password": "testpass123"
        })
        # Login succeeds
        response = await client.post("/auth/login", json={...})
        assert response.status_code == 200
    
    async def test_login_invalid_password(self, client):
        """POST /login - Returns HTTP 401 for wrong password"""
        response = await client.post("/auth/login", json={
            "email": "existing@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401
    
    async def test_protected_endpoint_requires_auth(self, client):
        """GET /me - Returns HTTP 401 without token"""
        response = await client.get("/auth/me")
        assert response.status_code == 401
    
    async def test_get_current_user_with_valid_token(self, client):
        """GET /me - Returns user info with valid JWT"""
        # Login first to get token
        login_response = await client.post("/auth/login", json={...})
        token = login_response.json()["access_token"]
        
        # Use token in Authorization header
        response = await client.get(
            "/auth/me", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "login_test@example.com"

# Run command: pytest tests/test_auth.py -v --tb=short
```

**Testing**:
- [ ] All 6 test cases pass (100% coverage of auth flow)
- [ ] Tests use in-memory SQLite database for isolation
- [ ] Each test is independent (no shared state between tests)

---

## 🖥️ Frontend Tasks (8 Atomic Tasks)

### **Task 5.9: Create Auth Store** ⏱️ ~30 min  
**Priority**: P0 - Critical Path  
**Dependencies**: None (can run in parallel with backend tasks)  
**Files to Create/Modify**:
- CREATE: `frontend/src/stores/auth.js`
- MODIFY: `frontend/src/main.ts` (register store plugin)

**Acceptance Criteria**:
```javascript
// stores/auth.js - Pinia authentication store
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref(null)
  
  // Computed properties
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // Actions
  async function login(email, password) {
    const response = await apiClient.post('/auth/login', { email, password })
    token.value = response.data.access_token
    localStorage.setItem('access_token', token.value)
    
    // Fetch user info
    await fetchUserInfo()
    return response.data
  }
  
  async function register(email, username, password) {
    const response = await apiClient.post('/auth/register', { 
      email, username, password 
    })
    token.value = response.data.access_token
    localStorage.setItem('access_token', token.value)
    
    await fetchUserInfo()
    return response.data
  }
  
  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const response = await apiClient.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      logout()
    }
  }
  
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    apiClient.defaults.headers.common['Authorization'] = undefined
  }
  
  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchUserInfo,
    logout
  }
})

// main.ts - Register store:
import { createPinia } from 'pinia'
const pinia = createPinia()
app.use(pinia)
```

**Testing**:
- [ ] Store can be imported in components (`const authStore = useAuthStore()`)
- [ ] Token persists across page refresh (localStorage working)
- [ ] `isAuthenticated` computed property updates automatically when token changes

---

### **Task 5.10: Update Axios Interceptors** ⏱️ ~25 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task 5.9 Complete  
**Files to Modify**:
- MODIFY: `frontend/src/api/client.ts`

**Acceptance Criteria**:
```typescript
// BEFORE (existing code):
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// AFTER (updated to use Pinia store):
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

apiClient.interceptors.request.use(config => {
  // Get auth store instance in request context
  const authStore = useAuthStore()
  const { token } = storeToRefs(authStore)
  
  if (token.value) {
    config.headers['Authorization'] = `Bearer ${token.value}`
  }
  return config
})

// Add response interceptor for automatic logout on 401:
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token invalid/expired - force logout
      const authStore = useAuthStore()
      authStore.logout()
      
      // Redirect to login page (handled by router guard)
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Add token refresh logic here in future Phase 5.2:
// if (error.response?.status === 401 && !retryAttempt.value) {
//   retryAttempt.value = true
//   return authStore.refreshToken().then(() => {
//     config.headers['Authorization'] = `Bearer ${authStore.token}`
//     return apiClient(config)
//   })
// }
```

**Testing**:
- [ ] All API requests automatically include JWT token in Authorization header
- [ ] 401 responses trigger automatic logout and redirect to /login
- [ ] Token removed from localStorage on logout

---

### **Task 5.11: Create Login Page Component** ⏱️ ~35 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task 5.9 Complete  
**Files to Create/Modify**:
- CREATE: `frontend/src/views/Login.vue`
- MODIFY: `frontend/src/router/index.ts` (add /login route)

**Acceptance Criteria**:
```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
    <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
      
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">🧘 瑜伽预约系统</h1>
        <p class="text-gray-600">登录您的账户继续</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        
        <!-- Email Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
          <input 
            v-model="formData.email"
            type="email" 
            required
            placeholder="admin@appt.local"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
          />
        </div>

        <!-- Password Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input 
            v-model="formData.password"
            type="password" 
            required
            placeholder="••••••••••••"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
          />
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <button 
          type="submit" 
          :disabled="isLoading"
          class="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>

      </form>

      <!-- Register Link -->
      <div class="mt-6 text-center">
        <p class="text-gray-600">
          还没有账户？ 
          <RouterLink to="/register" class="text-green-600 hover:text-green-700 font-medium">立即注册</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    await authStore.login(formData.value.email, formData.value.password)
    
    // Redirect to dashboard (or previous location)
    const redirect = router.currentRoute.value.query.redirect as string || '/admin/dashboard'
    router.push(redirect)
    
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查邮箱和密码'
    console.error('Login failed:', error)
  } finally {
    isLoading.value = false
  }
}

// Auto-login if already authenticated
if (authStore.isAuthenticated) {
  router.push('/admin/dashboard')
}
</script>
```

**Router Configuration**:
```typescript
// router/index.ts - Add login route:
{
  path: '/login',
  name: 'Login',
  component: () => import('@/views/Login.vue'),
  meta: { guestOnly: true }  // Redirect if already logged in
}
```

**Testing**:
- [ ] Form submits successfully with valid credentials (admin / ADMIN_PASSWORD)
- [ ] Invalid login shows error message "登录失败，请检查邮箱和密码"
- [ ] Successful login redirects to /admin/dashboard
- [ ] Already authenticated users redirected away from /login page
- [ ] "立即注册" link navigates to /register page

---

### **Task 5.12: Create Register Page Component** ⏱️ ~40 min  
**Priority**: P1 - Important  
**Dependencies**: Task 5.11 Complete (similar structure)  
**Files to Create/Modify**:
- CREATE: `frontend/src/views/Register.vue`
- MODIFY: `frontend/src/router/index.ts` (add /register route)

**Acceptance Criteria**:
```vue
<!-- Similar structure to Login.vue, but with additional fields -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
    <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
      
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">🧘 创建账户</h1>
        <p class="text-gray-600">注册开始预约瑜伽课程</p>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="space-y-5">
        
        <!-- Email Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
          <input 
            v-model="formData.email"
            type="email" 
            required
            placeholder="your@email.com"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
        </div>

        <!-- Username Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
          <input 
            v-model="formData.username"
            type="text" 
            required
            minlength="3"
            maxlength="100"
            placeholder="yoga_lover_2026"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
        </div>

        <!-- Password Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input 
            v-model="formData.password"
            type="password" 
            required
            minlength="8"
            placeholder="至少 8 个字符"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
        </div>

        <!-- Confirm Password Field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
          <input 
            v-model="formData.confirmPassword"
            type="password" 
            required
            placeholder="再次输入密码"
            :class="{ 'border-red-500': passwordMismatch }"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 outline-none transition"
          />
          <p v-if="passwordMismatch" class="mt-1 text-sm text-red-600">两次输入的密码不一致</p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <button 
          type="submit" 
          :disabled="isLoading || !!passwordMismatch"
          class="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5"
        >
          {{ isLoading ? '注册中...' : '注册并登录' }}
        </button>

      </form>

      <!-- Login Link -->
      <div class="mt-6 text-center">
        <p class="text-gray-600">
          已有账户？ 
          <RouterLink to="/login" class="text-green-600 hover:text-green-700 font-medium">立即登录</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

// Computed property for password validation
const passwordMismatch = computed(() => {
  return formData.value.password !== formData.value.confirmPassword
})

async function handleRegister() {
  if (passwordMismatch.value) return
  
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    await authStore.register(
      formData.value.email,
      formData.value.username,
      formData.value.password
    )
    
    // Auto-login after registration - redirect to home (not admin dashboard)
    router.push('/')
    
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '注册失败，请重试'
    console.error('Registration failed:', error)
  } finally {
    isLoading.value = false
  }
}

// Redirect if already authenticated  
if (authStore.isAuthenticated) {
  router.push('/')
}
</script>
```

**Router Configuration**:
```typescript
{
  path: '/register',
  name: 'Register',
  component: () => import('@/views/Register.vue'),
  meta: { guestOnly: true }
}
```

**Testing**:
- [ ] Email validation (must be valid email format)
- [ ] Username length validated (3-100 characters)
- [ ] Password minimum length enforced (8+ chars)
- [ ] Password confirmation mismatch shows error message
- [ ] Duplicate email rejected with clear error "邮箱已被注册"
- [ ] Successful registration auto-logins user and redirects to home page

---

### **Task 5.13: Implement Router Guards** ⏱️ ~25 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Tasks 5.9, 5.11, 5.12 Complete  
**Files to Modify**:
- MODIFY: `frontend/src/router/index.ts`

**Acceptance Criteria**:
```typescript
// router/index.ts - BEFORE (existing code):
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  
  if (to.meta.requiresAuth && !token) {
    console.warn('Warning: Admin access without authentication (testing mode)')
    next()  // TEMPORARILY DISABLED FOR TESTING - Remove in production!
    
    // Uncomment when login system ready:
    // next('/login')  
  } else {
    next()
  }
})

// router/index.ts - AFTER (full implementation):
import { useAuthStore } from '@/stores/auth'

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // If not authenticated yet but have token, fetch user info
  if (!authStore.isAuthenticated && localStorage.getItem('access_token')) {
    await authStore.fetchUserInfo()
  }

  // Route requires authentication?
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Redirect to login with return URL
      next({ 
        name: 'Login', 
        query: { redirect: to.fullPath } 
      })
      return
    }

    // Route requires admin role?
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // Not admin - go back or show error page
      next({ name: 'Home' })
      return
    }
  }

  // Route is for guests only (login/register pages)?
  if (to.meta.guestOnly) {
    if (authStore.isAuthenticated) {
      // Already logged in - redirect to dashboard or home
      const destination = authStore.isAdmin ? '/admin/dashboard' : '/'
      next(destination)
      return
    }
  }

  // All checks passed - proceed
  next()
})

// Update route definitions:
const routes: RouteRecordRaw[] = [
  { path: '/', component: Home, name: 'Home' },
  
  { 
    path: '/login', 
    component: () => import('@/views/Login.vue'), 
    name: 'Login',
    meta: { guestOnly: true }
  },
  
  { 
    path: '/register', 
    component: () => import('@/views/Register.vue'), 
    name: 'Register',
    meta: { guestOnly: true }
  },

  // Admin routes - require authentication + admin role
  { 
    path: '/admin/dashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    name: 'AdminDashboard',
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  
  // Regular user routes - only require authentication (optional)
  { 
    path: '/my-bookings',
    component: () => import('@/views/MyBookings.vue'),
    name: 'MyBookings',
    meta: { requiresAuth: false }  // Keep public for now
  },

  // Booking flow - keep public (no auth required yet)
  { 
    path: '/booking',
    component: () => import('@/views/BookingPage.vue'),
    name: 'Booking'
  }
]
```

**Testing**:
- [ ] Unauthenticated user accessing /admin/dashboard → Redirected to /login?returnUrl=/admin/dashboard
- [ ] Logged-in regular user accessing /admin/dashboard → Redirected to home page (403 behavior)
- [ ] Admin user can access all routes including admin pages
- [ ] Authenticated user accessing /login or /register → Redirected away from these pages
- [ ] After successful login, redirected to original intended destination

---

### **Task 5.14: Add Logout Button to Header** ⏱️ ~15 min  
**Priority**: P1 - Important  
**Dependencies**: Tasks 5.9, 5.13 Complete  
**Files to Modify**:
- MODIFY: `frontend/src/components/common/Header.vue`

**Acceptance Criteria**:
```vue
<!-- BEFORE (existing Header.vue without auth) -->
<template>
  <header class="bg-white shadow-sm border-b sticky top-0 z-50">
    <nav class="container mx-auto px-6 py-4 flex items-center justify-between">
      <!-- Logo and navigation links... -->
